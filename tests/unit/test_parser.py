from lexflow.core.parser import Parser


class TestParser:
    """Essential tests for Parser core functionality."""

    def test_parse_creates_program(self, sample_workflow):
        """Test that parser creates a valid AST program."""
        parser = Parser(sample_workflow, [sample_workflow])
        program = parser.parse()

        # Should create a valid program
        assert program is not None
        assert hasattr(program, "workflows")
        assert hasattr(program, "main")

    def test_parse_creates_main_statements(self, sample_workflow):
        """Test that parser creates main execution statements."""
        parser = Parser(sample_workflow, [sample_workflow])
        program = parser.parse()

        # Should have statements in main execution block
        assert len(program.main.statements) > 0

        # First statement should be workflow_start
        assert program.main.statements[0].opcode == "workflow_start"

    def test_parse_creates_node_map(self, sample_workflow):
        """Test that parser creates global node map."""
        parser = Parser(sample_workflow, [sample_workflow])
        program = parser.parse()

        # Should have global node map for node references
        assert hasattr(program, "node_map")
        assert isinstance(program.node_map, dict)
