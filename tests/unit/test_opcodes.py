"""Tests for OpcodeRegistry._format_type_hint and get_interface."""

from typing import Any, Dict, List, Optional, Union

from lexflow.opcodes import OpcodeRegistry


class TestFormatTypeHint:
    """Tests for _format_type_hint static method."""

    def test_simple_int(self):
        assert OpcodeRegistry._format_type_hint(int) == "int"

    def test_simple_str(self):
        assert OpcodeRegistry._format_type_hint(str) == "str"

    def test_simple_float(self):
        assert OpcodeRegistry._format_type_hint(float) == "float"

    def test_simple_bool(self):
        assert OpcodeRegistry._format_type_hint(bool) == "bool"

    def test_generic_list(self):
        assert OpcodeRegistry._format_type_hint(list[str]) == "list[str]"

    def test_generic_dict(self):
        result = OpcodeRegistry._format_type_hint(Dict[str, Any])
        assert result == "Dict[str, Any]"

    def test_optional(self):
        result = OpcodeRegistry._format_type_hint(Optional[int])
        assert "int" in result
        assert "Optional" in result or "None" in result

    def test_union(self):
        result = OpcodeRegistry._format_type_hint(Union[str, int])
        assert "str" in result
        assert "int" in result

    def test_any(self):
        assert OpcodeRegistry._format_type_hint(Any) == "Any"

    def test_generic_list_typing(self):
        result = OpcodeRegistry._format_type_hint(List[int])
        assert result == "List[int]"

    def test_none_type(self):
        assert OpcodeRegistry._format_type_hint(type(None)) == "NoneType"


class TestGetInterface:
    """Tests for get_interface method."""

    def _make_registry_with(self, func):
        """Create a fresh registry and register a single opcode."""
        registry = OpcodeRegistry()
        registry.register()(func)
        return registry

    def test_preserves_generic_return_type(self):
        async def my_op(x: int) -> list[str]:
            """Returns a list of strings."""
            return [str(x)]

        registry = self._make_registry_with(my_op)
        interface = registry.get_interface("my_op")
        assert interface["return_type"] == "list[str]"

    def test_preserves_generic_param_type(self):
        async def my_op(data: Dict[str, Any]) -> str:
            """Takes a dict param."""
            return ""

        registry = self._make_registry_with(my_op)
        interface = registry.get_interface("my_op")
        param = interface["parameters"][0]
        assert param["type"] == "Dict[str, Any]"

    def test_cleans_docstring(self):
        async def my_op(x: int) -> int:
            """Indented docstring.

            With extra whitespace that should be cleaned.
            """
            return x

        registry = self._make_registry_with(my_op)
        interface = registry.get_interface("my_op")
        doc = interface["doc"]
        assert doc is not None
        assert not doc.startswith(" ")
        assert not doc.startswith("\n")
        assert "Indented docstring." in doc

    def test_none_docstring(self):
        async def my_op(x: int) -> int:
            return x

        # Remove docstring explicitly
        my_op.__doc__ = None
        registry = self._make_registry_with(my_op)
        interface = registry.get_interface("my_op")
        assert interface["doc"] is None

    def test_unknown_opcode(self):
        registry = OpcodeRegistry()
        interface = registry.get_interface("nonexistent_op")
        assert "error" in interface
