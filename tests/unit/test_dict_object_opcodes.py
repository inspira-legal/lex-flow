"""Tests for dictionary and object opcodes."""

import pytest
from types import SimpleNamespace
from lexflow import default_registry

pytestmark = pytest.mark.asyncio


# ============ Dictionary Operation Tests ============

async def test_dict_create_empty():
    """Test creating empty dictionary."""
    result = await default_registry.call("dict_create", [])
    assert result == {}


async def test_dict_create_with_pairs():
    """Test creating dictionary with key-value pairs."""
    result = await default_registry.call("dict_create", ["a", 1, "b", 2, "c", 3])
    assert result == {"a": 1, "b": 2, "c": 3}


async def test_dict_create_odd_args():
    """Test that odd number of args raises error."""
    with pytest.raises(ValueError, match="even number of arguments"):
        await default_registry.call("dict_create", ["a", 1, "b"])


async def test_dict_from_lists():
    """Test creating dict from parallel lists."""
    keys = ["x", "y", "z"]
    values = [10, 20, 30]
    result = await default_registry.call("dict_from_lists", [keys, values])
    assert result == {"x": 10, "y": 20, "z": 30}


async def test_dict_set():
    """Test setting key-value pair."""
    d = {"a": 1}
    result = await default_registry.call("dict_set", [d, "b", 2])
    assert result == {"a": 1, "b": 2}
    assert result is d  # Mutates original


async def test_dict_set_overwrites():
    """Test that dict_set overwrites existing keys."""
    d = {"a": 1}
    result = await default_registry.call("dict_set", [d, "a", 99])
    assert result == {"a": 99}


async def test_dict_get():
    """Test getting value by key."""
    d = {"a": 1, "b": 2}
    result = await default_registry.call("dict_get", [d, "a"])
    assert result == 1


async def test_dict_get_with_default():
    """Test getting with default for missing key."""
    d = {"a": 1}
    result = await default_registry.call("dict_get", [d, "missing", "default"])
    assert result == "default"


async def test_dict_get_missing_no_default():
    """Test getting missing key without default returns None."""
    d = {"a": 1}
    result = await default_registry.call("dict_get", [d, "missing"])
    assert result is None


async def test_dict_pop():
    """Test removing and returning value."""
    d = {"a": 1, "b": 2}
    result = await default_registry.call("dict_pop", [d, "a"])
    assert result == 1
    assert d == {"b": 2}  # Mutates original


async def test_dict_pop_with_default():
    """Test pop with default for missing key."""
    d = {"a": 1}
    result = await default_registry.call("dict_pop", [d, "missing", "default"])
    assert result == "default"
    assert d == {"a": 1}  # Unchanged


async def test_dict_setdefault():
    """Test setdefault for existing key."""
    d = {"a": 1}
    result = await default_registry.call("dict_setdefault", [d, "a", 99])
    assert result == 1  # Returns existing value
    assert d == {"a": 1}  # Unchanged


async def test_dict_setdefault_new_key():
    """Test setdefault for new key."""
    d = {"a": 1}
    result = await default_registry.call("dict_setdefault", [d, "b", 2])
    assert result == 2
    assert d == {"a": 1, "b": 2}  # Added


async def test_dict_update():
    """Test updating with another dict."""
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 99, "c": 3}
    result = await default_registry.call("dict_update", [d1, d2])
    assert result == {"a": 1, "b": 99, "c": 3}
    assert result is d1  # Mutates d1


async def test_dict_clear():
    """Test clearing all items."""
    d = {"a": 1, "b": 2}
    result = await default_registry.call("dict_clear", [d])
    assert result == {}
    assert result is d  # Mutates original


async def test_dict_copy():
    """Test creating shallow copy."""
    d = {"a": 1, "b": 2}
    result = await default_registry.call("dict_copy", [d])
    assert result == {"a": 1, "b": 2}
    assert result is not d  # Different object


async def test_dict_keys():
    """Test getting list of keys."""
    d = {"a": 1, "b": 2, "c": 3}
    result = await default_registry.call("dict_keys", [d])
    assert set(result) == {"a", "b", "c"}


async def test_dict_values():
    """Test getting list of values."""
    d = {"a": 1, "b": 2, "c": 3}
    result = await default_registry.call("dict_values", [d])
    assert set(result) == {1, 2, 3}


async def test_dict_items():
    """Test getting list of (key, value) tuples."""
    d = {"a": 1, "b": 2}
    result = await default_registry.call("dict_items", [d])
    assert set(result) == {("a", 1), ("b", 2)}


async def test_dict_contains():
    """Test checking if key exists."""
    d = {"a": 1, "b": 2}
    assert await default_registry.call("dict_contains", [d, "a"]) is True
    assert await default_registry.call("dict_contains", [d, "missing"]) is False


async def test_dict_len():
    """Test getting number of items."""
    d = {"a": 1, "b": 2, "c": 3}
    result = await default_registry.call("dict_len", [d])
    assert result == 3


async def test_dict_is_empty():
    """Test checking if dict is empty."""
    assert await default_registry.call("dict_is_empty", [{}]) is True
    assert await default_registry.call("dict_is_empty", [{"a": 1}]) is False


async def test_dict_with_non_string_keys():
    """Test that dicts can use any hashable key type."""
    result = await default_registry.call("dict_create", [1, "one", 2, "two"])
    assert result == {1: "one", 2: "two"}


# ============ Object Operation Tests ============

async def test_object_create():
    """Test creating empty object."""
    result = await default_registry.call("object_create", [])
    assert isinstance(result, SimpleNamespace)
    assert vars(result) == {}


async def test_object_from_dict():
    """Test creating object from dictionary."""
    d = {"x": 10, "y": 20}
    result = await default_registry.call("object_from_dict", [d])
    assert isinstance(result, SimpleNamespace)
    assert result.x == 10
    assert result.y == 20


async def test_object_get_from_namespace():
    """Test getting attribute from SimpleNamespace."""
    obj = SimpleNamespace(a=1, b=2)
    result = await default_registry.call("object_get", [obj, "a"])
    assert result == 1


async def test_object_get_from_dict():
    """Test getting attribute from dict."""
    obj = {"a": 1, "b": 2}
    result = await default_registry.call("object_get", [obj, "a"])
    assert result == 1


async def test_object_get_with_default():
    """Test getting with default for missing attribute."""
    obj = SimpleNamespace(a=1)
    result = await default_registry.call("object_get", [obj, "missing", "default"])
    assert result == "default"


async def test_object_get_wrong_type():
    """Test that object_get raises TypeError for unsupported types."""
    with pytest.raises(TypeError, match="only works with SimpleNamespace or dict"):
        await default_registry.call("object_get", ["string", "attr"])


async def test_object_set_on_namespace():
    """Test setting attribute on SimpleNamespace."""
    obj = SimpleNamespace(a=1)
    result = await default_registry.call("object_set", [obj, "b", 2])
    assert result is obj  # Returns same object
    assert obj.b == 2


async def test_object_set_on_dict():
    """Test setting attribute on dict."""
    obj = {"a": 1}
    result = await default_registry.call("object_set", [obj, "b", 2])
    assert result is obj
    assert obj == {"a": 1, "b": 2}


async def test_object_set_wrong_type():
    """Test that object_set raises TypeError for unsupported types."""
    with pytest.raises(TypeError, match="only works with SimpleNamespace or dict"):
        await default_registry.call("object_set", ["string", "attr", "value"])


async def test_object_has_on_namespace():
    """Test checking if attribute exists on SimpleNamespace."""
    obj = SimpleNamespace(a=1, b=2)
    assert await default_registry.call("object_has", [obj, "a"]) is True
    assert await default_registry.call("object_has", [obj, "missing"]) is False


async def test_object_has_on_dict():
    """Test checking if key exists in dict."""
    obj = {"a": 1, "b": 2}
    assert await default_registry.call("object_has", [obj, "a"]) is True
    assert await default_registry.call("object_has", [obj, "missing"]) is False


async def test_object_remove_from_namespace():
    """Test removing attribute from SimpleNamespace."""
    obj = SimpleNamespace(a=1, b=2)
    result = await default_registry.call("object_remove", [obj, "a"])
    assert result is obj
    assert not hasattr(obj, "a")
    assert obj.b == 2


async def test_object_remove_from_dict():
    """Test removing key from dict."""
    obj = {"a": 1, "b": 2}
    result = await default_registry.call("object_remove", [obj, "a"])
    assert result is obj
    assert obj == {"b": 2}


async def test_object_remove_missing():
    """Test that removing missing attribute doesn't error."""
    obj = SimpleNamespace(a=1)
    result = await default_registry.call("object_remove", [obj, "missing"])
    assert result is obj  # No error


async def test_object_keys_from_namespace():
    """Test getting keys from SimpleNamespace."""
    obj = SimpleNamespace(a=1, b=2, _private=3)
    result = await default_registry.call("object_keys", [obj])
    assert set(result) == {"a", "b"}  # Filters _private


async def test_object_keys_from_dict():
    """Test getting keys from dict."""
    obj = {"a": 1, "b": 2, "c": 3}
    result = await default_registry.call("object_keys", [obj])
    assert set(result) == {"a", "b", "c"}


async def test_object_to_dict_from_namespace():
    """Test converting SimpleNamespace to dict."""
    obj = SimpleNamespace(a=1, b=2, _private=3)
    result = await default_registry.call("object_to_dict", [obj])
    assert result == {"a": 1, "b": 2}  # Filters _private
    assert isinstance(result, dict)


async def test_object_to_dict_from_dict():
    """Test converting dict to dict (copy)."""
    obj = {"a": 1, "b": 2}
    result = await default_registry.call("object_to_dict", [obj])
    assert result == {"a": 1, "b": 2}
    assert result is not obj  # Different object


async def test_object_dict_interop():
    """Test that objects and dicts work interchangeably."""
    # Create as object
    obj = await default_registry.call("object_create", [])
    await default_registry.call("object_set", [obj, "x", 10])

    # Convert to dict
    d = await default_registry.call("object_to_dict", [obj])
    assert d == {"x": 10}

    # Create object from dict
    obj2 = await default_registry.call("object_from_dict", [d])
    assert obj2.x == 10
