"""How opcodes treat a Secret: pass, reveal or taint (WAVE-989)."""

import io
from contextlib import asynccontextmanager

import pytest

from lexflow import Engine, OpcodeRegistry, Parser, Secret, default_registry, opcode
from lexflow import redact_secrets
from lexflow.opcodes import opcodes_http

pytestmark = pytest.mark.asyncio

VALUE = "s3cr3t-value"


def make_registry():
    """A registry with one opcode per mode that records what it received."""
    reg = OpcodeRegistry()
    seen = {}

    @reg.register(secret_mode="pass")
    async def t_pass(value, extra: dict = None):
        seen["pass"] = (value, extra)
        return value

    @reg.register(secret_mode="reveal")
    async def t_reveal(value, extra: dict = None):
        seen["reveal"] = (value, extra)
        return {"echo": value, "n": 1}

    @reg.register()
    async def t_taint(value, extra: dict = None):
        seen["taint"] = (value, extra)
        return {"echo": value, "list": [value, 3], "n": len(value)}

    @reg.register()
    async def t_fail(value):
        raise ValueError(f"bad value {value}")

    return reg, seen


class TestRegisterWrapper:
    async def test_pass_keeps_secret_objects(self):
        reg, seen = make_registry()
        secret = Secret(VALUE)
        result = await reg.call("t_pass", [secret], {"extra": {"h": secret}})
        assert result is secret
        assert seen["pass"][0] is secret
        assert seen["pass"][1]["h"] is secret

    async def test_reveal_deep_unwraps_and_leaves_result(self):
        reg, seen = make_registry()
        secret = Secret(VALUE)
        extra = {"headers": {"Authorization": secret}, "items": [secret, (secret,)]}
        result = await reg.call("t_reveal", [secret], {"extra": extra})
        value, got = seen["reveal"]
        assert value == VALUE and type(value) is str
        assert got == {"headers": {"Authorization": VALUE}, "items": [VALUE, (VALUE,)]}
        assert type(got["headers"]["Authorization"]) is str
        assert result == {"echo": VALUE, "n": 1}
        assert type(result["echo"]) is str
        # the caller's structure is untouched
        assert extra["headers"]["Authorization"] is secret

    async def test_taint_is_the_default(self):
        reg, _ = make_registry()
        assert reg.get_secret_mode("t_taint") == "taint"

    async def test_taint_wraps_text_results(self):
        reg, seen = make_registry()
        result = await reg.call("t_taint", [Secret(VALUE)])
        assert seen["taint"][0] == VALUE and type(seen["taint"][0]) is str
        assert isinstance(result["echo"], Secret)
        assert isinstance(result["list"][0], Secret)
        assert result["list"][1] == 3
        assert result["n"] == len(VALUE)
        assert redact_secrets(result) == {"echo": "***", "list": ["***", 3], "n": 12}

    async def test_taint_leaves_results_alone_without_secret(self):
        reg, _ = make_registry()
        result = await reg.call("t_taint", ["plain"])
        assert result["echo"] == "plain" and type(result["echo"]) is str

    async def test_arguments_without_secret_keep_identity(self):
        reg, seen = make_registry()
        extra = {"a": 1}
        await reg.call("t_taint", [Secret(VALUE)], {"extra": extra})
        assert seen["taint"][1] is extra

    async def test_exception_is_marked_when_secret_seen(self):
        reg, _ = make_registry()
        with pytest.raises(ValueError) as exc:
            await reg.call("t_fail", [Secret(VALUE)])
        assert getattr(exc.value, "__lexflow_secret__", False)

    async def test_exception_is_not_marked_without_secret(self):
        reg, _ = make_registry()
        with pytest.raises(ValueError) as exc:
            await reg.call("t_fail", ["plain"])
        assert not getattr(exc.value, "__lexflow_secret__", False)


class TestInjectWrapper:
    def make(self, mode):
        reg = OpcodeRegistry()

        @reg.register(privileged=True, secret_mode=mode)
        async def priv(value) -> str:
            pass

        seen = {}

        async def impl(value):
            seen["value"] = value
            return f"got {value}"

        reg.inject("priv", impl)
        return reg, seen

    async def test_taint(self):
        reg, seen = self.make(None)
        result = await reg.call("priv", [Secret(VALUE)])
        assert type(seen["value"]) is str
        assert isinstance(result, Secret) and result.reveal() == f"got {VALUE}"

    async def test_reveal(self):
        reg, seen = self.make("reveal")
        result = await reg.call("priv", [Secret(VALUE)])
        assert type(seen["value"]) is str
        assert result == f"got {VALUE}" and type(result) is str

    async def test_pass(self):
        reg, seen = self.make("pass")
        result = await reg.call("priv", [Secret(VALUE)])
        assert isinstance(seen["value"], Secret)
        assert result == "got ***"


class TestDeclaringModes:
    async def test_set_secret_mode_overrides_by_name(self):
        reg, seen = make_registry()
        reg.set_secret_mode("t_taint", "reveal")
        result = await reg.call("t_taint", [Secret(VALUE)])
        assert type(result["echo"]) is str
        reg.set_secret_mode("t_taint", "pass")
        with pytest.raises(TypeError):
            await reg.call("t_taint", [Secret(VALUE)])  # len(Secret)

    async def test_set_secret_mode_unknown_opcode(self):
        reg, _ = make_registry()
        with pytest.raises(ValueError, match="Unknown opcode"):
            reg.set_secret_mode("nope", "reveal")

    async def test_invalid_mode(self):
        reg, _ = make_registry()
        with pytest.raises(ValueError, match="secret_mode"):
            reg.set_secret_mode("t_taint", "hide")
        with pytest.raises(ValueError, match="secret_mode"):
            reg.register(secret_mode="hide")

    async def test_opcode_helper_accepts_mode(self):
        @opcode(secret_mode="reveal")
        async def _test_secret_helper_op(value) -> str:
            """Test opcode."""
            return value

        try:
            assert (
                default_registry.get_secret_mode("_test_secret_helper_op") == "reveal"
            )
        finally:
            default_registry.opcodes.pop("_test_secret_helper_op")
            default_registry.signatures.pop("_test_secret_helper_op")
            default_registry.secret_modes.pop("_test_secret_helper_op")


class TestCoreClassification:
    @pytest.mark.parametrize(
        "name",
        ["dict_get", "list_append", "object_get", "io_print", "throw", "assert_equals"]
        + ["channel_send", "task_result", "print_info", "workflow_start"],
    )
    async def test_pass(self, name):
        assert default_registry.get_secret_mode(name) == "pass"

    @pytest.mark.parametrize(
        "name",
        [n for n in default_registry.list_opcodes() if n.startswith("http_")]
        + [n for n in default_registry.list_opcodes() if n.endswith("_create_client")],
    )
    async def test_reveal(self, name):
        assert default_registry.get_secret_mode(name) == "reveal"

    @pytest.mark.parametrize(
        "name",
        ["operator_add", "str", "string_join", "json_stringify", "json_parse"],
    )
    async def test_taint(self, name):
        assert default_registry.get_secret_mode(name) == "taint"


class TestCoreOpcodes:
    async def call(self, name, *args):
        return await default_registry.call(name, list(args))

    async def test_dict_get_returns_the_secret(self):
        secret = Secret(VALUE)
        assert await self.call("dict_get", {"K": secret}, "K") is secret

    async def test_operator_add_taints(self):
        result = await self.call("operator_add", "Bearer ", Secret(VALUE))
        assert isinstance(result, Secret)
        assert result.reveal() == f"Bearer {VALUE}"
        assert str(result) == "***"

    async def test_operator_equals_returns_plain_bool(self):
        assert await self.call("operator_equals", Secret(VALUE), VALUE) is True
        assert await self.call("operator_equals", Secret(VALUE), "x") is False

    async def test_to_string_taints(self):
        result = await self.call("str", Secret(VALUE))
        assert isinstance(result, Secret) and result.reveal() == VALUE

    async def test_string_join_taints(self):
        result = await self.call("string_join", ["a", Secret(VALUE)], "-")
        assert isinstance(result, Secret) and result.reveal() == f"a-{VALUE}"

    async def test_string_split_returns_list_of_secrets(self):
        result = await self.call("string_split", Secret("a b"))
        assert all(isinstance(p, Secret) for p in result)
        assert [p.reveal() for p in result] == ["a", "b"]

    async def test_string_length_is_plain_number(self):
        assert await self.call("string_length", Secret(VALUE)) == len(VALUE)

    async def test_json_stringify_taints(self):
        result = await self.call("json_stringify", {"k": Secret(VALUE)})
        assert isinstance(result, Secret)
        assert VALUE in result.reveal()

    async def test_json_parse_keeps_keys_and_taints_values(self):
        parsed = await self.call("json_parse", Secret('{"private_key": "pk", "n": 1}'))
        assert list(parsed) == ["private_key", "n"]
        assert type(next(iter(parsed))) is str
        value = await self.call("dict_get", parsed, "private_key")
        assert isinstance(value, Secret) and value.reveal() == "pk"
        assert parsed["n"] == 1

    async def test_list_contains_compares_value(self):
        assert await self.call("list_contains", ["a", VALUE], Secret(VALUE)) is True

    async def test_assert_equals_message_hides_value(self):
        with pytest.raises(AssertionError) as exc:
            await self.call("assert_equals", Secret(VALUE), "x")
        assert VALUE not in str(exc.value)

    async def test_throw_message_hides_value(self):
        with pytest.raises(RuntimeError) as exc:
            await self.call("throw", Secret(VALUE))
        assert str(exc.value) == "***"


class FakeResponse:
    status = 200
    headers = {"Content-Type": "text/plain"}

    async def text(self):
        return "ok"

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class TestHttpReveal:
    async def test_http_get_sends_real_header_values(self, monkeypatch):
        sent = {}

        class FakeSession:
            def get(self, url, headers=None):
                sent["url"], sent["headers"] = url, headers
                return FakeResponse()

        @asynccontextmanager
        async def fake_open_session(**kwargs):
            yield FakeSession()

        monkeypatch.setattr(opcodes_http, "open_session", fake_open_session)
        secret = Secret(VALUE)
        headers = {"Authorization": await self_add("Bearer ", secret)}
        result = await default_registry.call(
            "http_get", ["https://api.example.com"], {"headers": headers}
        )
        assert sent["headers"] == {"Authorization": f"Bearer {VALUE}"}
        assert type(sent["headers"]["Authorization"]) is str
        assert result["text"] == "ok" and type(result["text"]) is str
        assert isinstance(headers["Authorization"], Secret)


async def self_add(left, right):
    return await default_registry.call("operator_add", [left, right])


def run(workflow, inputs=None, output=None):
    program = Parser().parse_dict(workflow)
    return Engine(program, output=output).run(inputs=inputs)


ENV_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": ["_env"], "outputs": []},
            "variables": {"_env": {}},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "print"},
                "print": {
                    "opcode": "io_print",
                    "next": "call",
                    "inputs": {
                        "STRING": {
                            "node": "get_key",
                        }
                    },
                },
                "get_key": {
                    "opcode": "dict_get",
                    "isReporter": True,
                    "args": [{"variable": "_env"}, {"literal": "API_KEY"}],
                },
                "call": {
                    "opcode": "workflow_call",
                    "next": "ret",
                    "kwargs": {
                        "workflow": {"literal": "check"},
                        "env": {"variable": "_env"},
                    },
                },
                "ret": {
                    "opcode": "workflow_return",
                    "kwargs": {"value": {"variable": "_env"}},
                },
            },
        },
        {
            "name": "check",
            "interface": {"inputs": ["env"], "outputs": []},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "if"},
                "if": {
                    "opcode": "control_if",
                    "kwargs": {
                        "condition": {"node": "get"},
                        "then": {"branch": "print"},
                    },
                },
                "get": {
                    "opcode": "dict_get",
                    "isReporter": True,
                    "args": [{"variable": "env"}, {"literal": "API_KEY"}],
                },
                "print": {
                    "opcode": "io_print",
                    "args": [{"literal": " truthy"}],
                },
            },
        },
    ]
}


CATCH_WORKFLOW = {
    "workflows": [
        {
            "name": "main",
            "interface": {"inputs": ["_env"], "outputs": []},
            "variables": {"_env": {}, "err": ""},
            "nodes": {
                "start": {"opcode": "workflow_start", "next": "try"},
                "try": {
                    "opcode": "control_try",
                    "next": "ret",
                    "kwargs": {
                        "try": {"branch": "convert"},
                        "catch": [{"var": "err", "body": {"branch": "noop"}}],
                    },
                },
                "convert": {
                    "opcode": "int",
                    "args": [{"node": "get"}],
                },
                "get": {
                    "opcode": "dict_get",
                    "isReporter": True,
                    "args": [{"variable": "_env"}, {"literal": "API_KEY"}],
                },
                "noop": {"opcode": "noop"},
                "ret": {
                    "opcode": "workflow_return",
                    "kwargs": {"value": {"variable": "err"}},
                },
            },
        }
    ]
}


class TestWorkflow:
    async def test_returned_env_redacts_to_mask(self):
        env = {"API_KEY": Secret(VALUE), "REGION": "us"}
        out = io.StringIO()
        result = await run(ENV_WORKFLOW, {"_env": env}, out)
        assert result is env
        assert result["API_KEY"] is env["API_KEY"]
        assert redact_secrets(result) == {"API_KEY": "***", "REGION": "us"}
        assert out.getvalue() == "*** truthy"
        assert VALUE not in out.getvalue()
        assert isinstance(env["API_KEY"], Secret)

    async def test_catch_variable_is_secret(self):
        env = {"API_KEY": Secret(VALUE)}
        result = await run(CATCH_WORKFLOW, {"_env": env})
        assert isinstance(result, Secret)
        assert VALUE in result.reveal()
        assert redact_secrets({"error": result}) == {"error": "***"}

    async def test_catch_variable_plain_without_secret(self):
        result = await run(CATCH_WORKFLOW, {"_env": {"API_KEY": "abc"}})
        assert type(result) is str and "abc" in result
