"""Tests for the description field on CategoryInfo and OpcodeRegistry."""

import pytest
from lexflow.opcodes.opcodes import CategoryInfo, OpcodeRegistry


class TestCategoryInfoDescription:
    def test_default_description_is_empty(self):
        cat = CategoryInfo(id="test", label="Test", prefix="test_")
        assert cat.description == ""

    def test_description_is_stored(self):
        cat = CategoryInfo(id="test", label="Test", prefix="test_", description="Uma descricao")
        assert cat.description == "Uma descricao"

    def test_to_dict_includes_description(self):
        cat = CategoryInfo(id="test", label="Test", prefix="test_", description="Descricao")
        d = cat.to_dict()
        assert "description" in d
        assert d["description"] == "Descricao"

    def test_to_dict_includes_empty_description(self):
        cat = CategoryInfo(id="test", label="Test", prefix="test_")
        d = cat.to_dict()
        assert "description" in d
        assert d["description"] == ""


class TestRegisterCategoryDescription:
    def test_register_category_with_description(self):
        reg = OpcodeRegistry()
        reg.register_category(id="test", label="Test", prefix="test_", description="Descricao teste")
        cat = reg.categories["test"]
        assert cat.description == "Descricao teste"

    def test_register_category_without_description(self):
        reg = OpcodeRegistry()
        reg.register_category(id="test", label="Test", prefix="test_")
        cat = reg.categories["test"]
        assert cat.description == ""


class TestOpcodeDescription:
    def test_register_opcode_with_description(self):
        reg = OpcodeRegistry()
        reg.register_category(id="test", label="Test", prefix="test_")

        @reg.register(category="test", description="Faz algo util")
        async def test_do_something(x: int) -> int:
            """Do something useful."""
            return x

        assert "test_do_something" in reg.descriptions
        assert reg.descriptions["test_do_something"] == "Faz algo util"

    def test_register_opcode_without_description(self):
        reg = OpcodeRegistry()
        reg.register_category(id="test", label="Test", prefix="test_")

        @reg.register(category="test")
        async def test_no_desc(x: int) -> int:
            """No description provided."""
            return x

        assert "test_no_desc" not in reg.descriptions

    def test_get_interface_includes_description(self):
        reg = OpcodeRegistry()
        reg.register_category(id="test", label="Test", prefix="test_")

        @reg.register(category="test", description="Descricao do opcode")
        async def test_with_desc(x: int) -> int:
            """Technical docstring."""
            return x

        interface = reg.get_interface("test_with_desc")
        assert interface["description"] == "Descricao do opcode"
        assert interface["doc"] == "Technical docstring."

    def test_get_interface_without_description(self):
        reg = OpcodeRegistry()
        reg.register_category(id="test", label="Test", prefix="test_")

        @reg.register(category="test")
        async def test_no_desc2(x: int) -> int:
            """Technical docstring only."""
            return x

        interface = reg.get_interface("test_no_desc2")
        assert "description" not in interface
        assert interface["doc"] == "Technical docstring only."
