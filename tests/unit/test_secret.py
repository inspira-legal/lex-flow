"""The Secret type and the helpers that walk structures holding it (WAVE-989)."""

import copy
import json
from types import SimpleNamespace

import pytest

from lexflow import Secret, redact_secrets
from lexflow.secret import contains_secret, reveal_secrets, taint

VALUE = "s3cr3t-value"


class TestSecret:
    def test_never_shows_itself(self):
        s = Secret(VALUE)
        assert str(s) == "***"
        assert repr(s) == "***"
        assert f"{s}" == "***"
        assert format(s, ">5") == "  ***"
        assert "%s" % s == "***"
        assert VALUE not in repr([s, {"k": s}])

    def test_reveal_returns_real_value(self):
        assert Secret(VALUE).reveal() == VALUE

    def test_wrapping_a_secret_keeps_the_value(self):
        assert Secret(Secret(VALUE)).reveal() == VALUE

    def test_is_not_a_str(self):
        assert not isinstance(Secret(VALUE), str)

    def test_only_wraps_str(self):
        with pytest.raises(TypeError):
            Secret(123)

    def test_bool_is_value_non_empty(self):
        assert bool(Secret(VALUE)) is True
        assert bool(Secret("")) is False

    def test_equality_compares_value(self):
        assert Secret(VALUE) == Secret(VALUE)
        assert Secret(VALUE) == VALUE
        assert VALUE == Secret(VALUE)
        assert Secret(VALUE) != "other"
        assert Secret(VALUE) != 1
        assert VALUE in [Secret(VALUE)]
        assert Secret(VALUE) in ["a", VALUE]

    def test_hash_is_value_hash(self):
        assert hash(Secret(VALUE)) == hash(VALUE)
        assert {"k": 1}[Secret("k")] == 1
        assert len({Secret(VALUE), VALUE}) == 1

    def test_immutable(self):
        s = Secret(VALUE)
        with pytest.raises(AttributeError):
            s._value = "x"
        with pytest.raises(AttributeError):
            del s._value
        with pytest.raises(AttributeError):
            s.other = "x"

    def test_json_dumps_never_emits_value(self):
        with pytest.raises(TypeError) as exc:
            json.dumps({"k": Secret(VALUE)})
        assert VALUE not in str(exc.value)

    def test_copies_stay_secret(self):
        s = Secret(VALUE)
        assert copy.copy(s).reveal() == VALUE
        assert copy.deepcopy({"k": s})["k"].reveal() == VALUE


class TestRedactSecrets:
    def test_replaces_every_secret(self):
        ns = SimpleNamespace(token=Secret(VALUE), plain="p")
        data = {
            "a": Secret(VALUE),
            "b": [Secret(VALUE), "x", (Secret(VALUE), 1)],
            "c": {Secret(VALUE), "y"},
            "d": ns,
            "e": 5,
        }
        out = redact_secrets(data)
        assert out["a"] == "***"
        assert out["b"] == ["***", "x", ("***", 1)]
        assert out["c"] == {"***", "y"}
        assert vars(out["d"]) == {"token": "***", "plain": "p"}
        assert out["e"] == 5
        assert VALUE not in json.dumps(
            {k: v for k, v in out.items() if k != "c"}, default=vars
        )

    def test_never_mutates_input(self):
        secret = Secret(VALUE)
        inner = [secret]
        ns = SimpleNamespace(token=secret)
        data = {"k": secret, "inner": inner, "ns": ns}
        out = redact_secrets(data)
        assert data["k"] is secret
        assert inner == [secret] and inner[0] is secret
        assert ns.token is secret
        assert out is not data and out["inner"] is not inner and out["ns"] is not ns

    def test_top_level_secret(self):
        assert redact_secrets(Secret(VALUE)) == "***"

    def test_dict_keys_are_left_alone(self):
        assert redact_secrets({"KEY": Secret(VALUE)}) == {"KEY": "***"}

    def test_plain_values_unchanged(self):
        assert redact_secrets({"a": [1, "b", None]}) == {"a": [1, "b", None]}

    def test_cyclic_structure(self):
        data = {"k": Secret(VALUE)}
        data["self"] = data
        out = redact_secrets(data)
        assert out["k"] == "***"
        assert out["self"] is out


class TestHelpers:
    def test_contains_secret(self):
        assert contains_secret({"a": [(Secret(VALUE),)]})
        assert contains_secret(SimpleNamespace(x={Secret(VALUE)}))
        assert not contains_secret({"a": [1, "b"]})

    def test_contains_secret_ignores_keys(self):
        assert not contains_secret({Secret(VALUE): 1})

    def test_reveal_keeps_identity_without_secrets(self):
        data = {"a": [1]}
        assert reveal_secrets(data) is data

    def test_reveal_builds_new_containers(self):
        data = {"h": {"Authorization": Secret(VALUE)}}
        out = reveal_secrets(data)
        assert out == {"h": {"Authorization": VALUE}}
        assert type(out["h"]["Authorization"]) is str
        assert isinstance(data["h"]["Authorization"], Secret)

    def test_taint_wraps_every_str(self):
        out = taint({"k": ["a", 1, ("b",), {"c"}], "n": 2.5, "b": True})
        assert isinstance(out["k"][0], Secret)
        assert out["k"][1] == 1
        assert isinstance(out["k"][2][0], Secret)
        assert all(isinstance(v, Secret) for v in out["k"][3])
        assert out["n"] == 2.5 and out["b"] is True
        assert all(type(k) is str for k in out)
