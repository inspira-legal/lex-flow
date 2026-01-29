"""Tests for the grammar module - the single source of truth for LexFlow constructs."""

import pytest
from lexflow.grammar import (
    get_grammar,
    get_construct,
    get_category,
    get_control_flow_opcodes,
    get_branch_color,
    get_node_color,
    get_reporter_color,
    is_control_flow_opcode,
    get_construct_branches,
    get_construct_inputs,
)


class TestGetGrammar:
    """Tests for get_grammar function."""

    def test_returns_valid_grammar(self):
        """Grammar should have required top-level keys."""
        grammar = get_grammar()
        assert "version" in grammar
        assert "categories" in grammar
        assert "constructs" in grammar
        assert "branch_colors" in grammar
        assert "node_colors" in grammar
        assert "reporter_colors" in grammar

    def test_grammar_has_categories(self):
        """Grammar should have at least the core categories."""
        grammar = get_grammar()
        category_ids = {c["id"] for c in grammar["categories"]}
        assert "control" in category_ids
        assert "data" in category_ids
        assert "io" in category_ids
        assert "operator" in category_ids

    def test_grammar_has_constructs(self):
        """Grammar should have the core control flow constructs."""
        grammar = get_grammar()
        opcodes = {c["opcode"] for c in grammar["constructs"]}
        assert "control_if" in opcodes
        assert "control_if_else" in opcodes
        assert "control_while" in opcodes
        assert "control_for" in opcodes
        assert "control_foreach" in opcodes
        assert "control_try" in opcodes

    def test_categories_have_required_fields(self):
        """Each category should have required fields."""
        grammar = get_grammar()
        for category in grammar["categories"]:
            assert "id" in category
            assert "prefix" in category
            assert "label" in category
            assert "color" in category
            assert "icon" in category

    def test_constructs_have_required_fields(self):
        """Each construct should have required fields."""
        grammar = get_grammar()
        for construct in grammar["constructs"]:
            assert "opcode" in construct
            assert "display_name" in construct
            assert "ast_class" in construct
            assert "category" in construct
            assert "description" in construct
            assert "inputs" in construct
            assert "branches" in construct


class TestGetConstruct:
    """Tests for get_construct function."""

    def test_get_existing_construct(self):
        """Should return construct for valid opcode."""
        construct = get_construct("control_if")
        assert construct is not None
        assert construct["opcode"] == "control_if"
        assert construct["ast_class"] == "If"

    def test_get_nonexistent_construct(self):
        """Should return None for invalid opcode."""
        construct = get_construct("nonexistent_opcode")
        assert construct is None

    def test_control_if_has_then_branch(self):
        """control_if should have THEN branch."""
        construct = get_construct("control_if")
        branch_names = [b["name"] for b in construct["branches"]]
        assert "THEN" in branch_names

    def test_control_if_else_has_both_branches(self):
        """control_if_else should have THEN and ELSE branches."""
        construct = get_construct("control_if_else")
        branch_names = [b["name"] for b in construct["branches"]]
        assert "THEN" in branch_names
        assert "ELSE" in branch_names

    def test_control_while_has_body_branch(self):
        """control_while should have BODY branch."""
        construct = get_construct("control_while")
        branch_names = [b["name"] for b in construct["branches"]]
        assert "BODY" in branch_names

    def test_control_for_has_loop_inputs(self):
        """control_for should have VAR, START, END inputs."""
        construct = get_construct("control_for")
        input_names = [i["name"] for i in construct["inputs"]]
        assert "VAR" in input_names
        assert "START" in input_names
        assert "END" in input_names


class TestGetCategory:
    """Tests for get_category function."""

    def test_get_existing_category(self):
        """Should return category for valid ID."""
        category = get_category("control")
        assert category is not None
        assert category["id"] == "control"
        assert category["prefix"] == "control_"

    def test_get_nonexistent_category(self):
        """Should return None for invalid ID."""
        category = get_category("nonexistent")
        assert category is None


class TestGetControlFlowOpcodes:
    """Tests for get_control_flow_opcodes function."""

    def test_returns_set_of_opcodes(self):
        """Should return a set of control flow opcodes."""
        opcodes = get_control_flow_opcodes()
        assert isinstance(opcodes, set)
        assert len(opcodes) > 0

    def test_contains_core_control_flow(self):
        """Should contain core control flow opcodes."""
        opcodes = get_control_flow_opcodes()
        assert "control_if" in opcodes
        assert "control_if_else" in opcodes
        assert "control_while" in opcodes
        assert "control_for" in opcodes

    def test_does_not_contain_non_branching_opcodes(self):
        """Should not contain opcodes without branches."""
        opcodes = get_control_flow_opcodes()
        # control_throw has no branches
        assert "control_throw" not in opcodes


class TestGetBranchColor:
    """Tests for get_branch_color function."""

    def test_then_branch_color(self):
        """THEN branch should have green color."""
        color = get_branch_color("THEN")
        assert color == "#34D399"

    def test_else_branch_color(self):
        """ELSE branch should have red color."""
        color = get_branch_color("ELSE")
        assert color == "#F87171"

    def test_body_branch_color(self):
        """BODY branch should have cyan color."""
        color = get_branch_color("BODY")
        assert color == "#22D3EE"

    def test_catch_branches_have_same_color(self):
        """All CATCH branches should have the same color."""
        color1 = get_branch_color("CATCH")
        color2 = get_branch_color("CATCH1")
        color3 = get_branch_color("CATCH2")
        assert color1 == color2 == color3

    def test_unknown_branch_returns_default(self):
        """Unknown branch should return default color."""
        color = get_branch_color("UNKNOWN_BRANCH")
        assert color is not None


class TestGetNodeColor:
    """Tests for get_node_color function."""

    def test_control_flow_color(self):
        """control_flow should have orange color."""
        color = get_node_color("control_flow")
        assert color == "#FF9500"

    def test_data_color(self):
        """data should have green color."""
        color = get_node_color("data")
        assert color == "#4CAF50"

    def test_unknown_type_returns_default(self):
        """Unknown type should return opcode default color."""
        color = get_node_color("unknown_type")
        assert color == "#64748B"


class TestGetReporterColor:
    """Tests for get_reporter_color function."""

    def test_data_opcode_color(self):
        """data_ prefixed opcodes should have data color."""
        color = get_reporter_color("data_get_variable")
        assert color == "#4CAF50"

    def test_operator_opcode_color(self):
        """operator_ prefixed opcodes should have operator color."""
        color = get_reporter_color("operator_add")
        assert color == "#9C27B0"

    def test_unknown_opcode_returns_default(self):
        """Unknown opcode prefix should return default color."""
        color = get_reporter_color("unknown_opcode")
        assert color == "#64748B"


class TestIsControlFlowOpcode:
    """Tests for is_control_flow_opcode function."""

    def test_control_if_is_control_flow(self):
        """control_if should be a control flow opcode."""
        assert is_control_flow_opcode("control_if") is True

    def test_control_while_is_control_flow(self):
        """control_while should be a control flow opcode."""
        assert is_control_flow_opcode("control_while") is True

    def test_io_print_is_not_control_flow(self):
        """io_print should not be a control flow opcode."""
        assert is_control_flow_opcode("io_print") is False

    def test_control_throw_is_not_control_flow(self):
        """control_throw has no branches, so not control flow."""
        assert is_control_flow_opcode("control_throw") is False


class TestGetConstructBranches:
    """Tests for get_construct_branches function."""

    def test_control_if_branches(self):
        """control_if should have THEN branch."""
        branches = get_construct_branches("control_if")
        assert len(branches) == 1
        assert branches[0]["name"] == "THEN"

    def test_control_if_else_branches(self):
        """control_if_else should have THEN and ELSE branches."""
        branches = get_construct_branches("control_if_else")
        assert len(branches) == 2
        names = [b["name"] for b in branches]
        assert "THEN" in names
        assert "ELSE" in names

    def test_nonexistent_opcode_returns_empty(self):
        """Nonexistent opcode should return empty list."""
        branches = get_construct_branches("nonexistent")
        assert branches == []


class TestGetConstructInputs:
    """Tests for get_construct_inputs function."""

    def test_control_if_inputs(self):
        """control_if should have CONDITION input."""
        inputs = get_construct_inputs("control_if")
        assert len(inputs) >= 1
        names = [i["name"] for i in inputs]
        assert "CONDITION" in names

    def test_control_for_inputs(self):
        """control_for should have VAR, START, END, STEP inputs."""
        inputs = get_construct_inputs("control_for")
        names = [i["name"] for i in inputs]
        assert "VAR" in names
        assert "START" in names
        assert "END" in names
        assert "STEP" in names

    def test_nonexistent_opcode_returns_empty(self):
        """Nonexistent opcode should return empty list."""
        inputs = get_construct_inputs("nonexistent")
        assert inputs == []
