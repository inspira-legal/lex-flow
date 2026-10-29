"""The Secret type and the helpers that walk structures holding it (WAVE-989)."""

import copy
import json
import pickle
from collections import OrderedDict, defaultdict, namedtuple
from types import SimpleNamespace

import pytest

from lexflow.secret import (
    Secret,
    contains_secret,
    is_secret_exception,
    mark_secret_exception,
    redact_secrets,
    reveal_secrets,
    taint,
)

Point = namedtuple("Point", "x y")


def deep(levels, leaf):
    value = leaf
    for _ in range(levels):
        value = [value]
    return value


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
        assert copy.copy(s) is s
        assert copy.deepcopy({"k": s})["k"] is s

    @pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
    def test_pickle_refuses_without_value(self, protocol):
        with pytest.raises(TypeError) as exc:
            pickle.dumps({"k": Secret(VALUE)}, protocol=protocol)
        assert VALUE not in str(exc.value)


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

    def test_contains_secret_sees_keys(self):
        assert contains_secret({Secret(VALUE): 1})
        assert contains_secret({(1, Secret(VALUE)): 1})

    def test_reveal_unwraps_keys(self):
        out = reveal_secrets({Secret("k"): Secret(VALUE)})
        assert out == {"k": VALUE}
        assert all(type(k) is str for k in out)

    def test_taint_keeps_keys(self):
        key = Secret("k")
        out = taint({key: "v", "plain": 1})
        assert next(iter(out)) is key
        assert type(list(out)[1]) is str

    def test_redact_masks_keys(self):
        assert redact_secrets({Secret("k"): 1, "a": 2}) == {"***": 1, "a": 2}

    def test_clean_subcontainers_keep_identity_and_type(self):
        od = OrderedDict(a=1)
        dd = defaultdict(list, a=[1])
        pt = Point(1, 2)

        class Tags(set):
            pass

        tags = Tags({1})
        data = {"s": Secret(VALUE), "od": od, "dd": dd, "pt": pt, "tags": tags}
        for out in (reveal_secrets(data), redact_secrets(data)):
            assert out is not data
            assert out["od"] is od and out["dd"] is dd
            assert out["pt"] is pt and out["tags"] is tags

    def test_changed_subclasses_become_base_type(self):
        out = reveal_secrets(OrderedDict(a=Secret(VALUE)))
        assert type(out) is dict and out == {"a": VALUE}
        out = reveal_secrets(Point(Secret(VALUE), 2))
        assert type(out) is tuple and out == (VALUE, 2)

    def test_taint_keeps_containers_without_text(self):
        data = {"n": [1, 2.5, None], "t": (True,)}
        out = taint(data)
        assert out is data

    def test_deep_nesting_does_not_recurse(self):
        plain = deep(5000, 1)
        assert not contains_secret(plain)
        assert reveal_secrets(plain) is plain
        assert redact_secrets(plain) is plain
        assert taint(plain) is plain
        hidden = deep(5000, Secret(VALUE))
        assert contains_secret(hidden)
        out = reveal_secrets(hidden)
        for _ in range(5000):
            out = out[0]
        assert out == VALUE and type(out) is str
        tainted = taint(deep(5000, "x"))
        for _ in range(5000):
            tainted = tainted[0]
        assert isinstance(tainted, Secret)

    def test_cycle_through_tuple_and_list(self):
        lst = [Secret(VALUE)]
        tup = (lst, 1)
        lst.append(tup)
        out = reveal_secrets(tup)
        assert out[0][0] == VALUE and type(out[0][0]) is str
        assert out[0][1] is out
        assert isinstance(lst[0], Secret)

    def test_cycle_tuple_list_tuple(self):
        lst = [Secret(VALUE)]
        t1 = (lst,)
        t2 = (t1,)
        lst.append(t2)
        out = redact_secrets(t1)
        assert out[0][0] == "***"
        assert out[0][1][0] is out


class TestExceptionMark:
    def test_mark_and_read(self):
        e = ValueError("x")
        assert not is_secret_exception(e)
        mark_secret_exception(e)
        assert is_secret_exception(e)

    def test_mark_never_raises(self):
        class Locked(Exception):
            def __setattr__(self, name, value):
                raise AttributeError("locked")

        e = Locked("x")
        mark_secret_exception(e)
        assert not is_secret_exception(e)

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
