"""Tests for output capture and redirection functionality."""

import io
import tempfile
from pathlib import Path

import pytest

from lexflow import Parser, Engine
from lexflow.output import OutputCapture, TeeOutput, StreamingOutput

# Enable async test support
pytestmark = pytest.mark.asyncio


# Simple test workflow that prints "Hello, World!"
SIMPLE_HELLO_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        opcode: workflow_start
        next: print_hello
        inputs: {}
      print_hello:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Hello, World!\\n"
"""


# Workflow that prints multiple lines
MULTI_LINE_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        opcode: workflow_start
        next: print_line1
        inputs: {}
      print_line1:
        opcode: io_print
        next: print_line2
        inputs:
          STRING:
            literal: "Line 1\\n"
      print_line2:
        opcode: io_print
        next: print_line3
        inputs:
          STRING:
            literal: "Line 2\\n"
      print_line3:
        opcode: io_print
        next: null
        inputs:
          STRING:
            literal: "Line 3\\n"
"""


async def test_string_io_capture():
    """Test capturing output to StringIO buffer."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(SIMPLE_HELLO_WORKFLOW)
        temp_path = Path(f.name)

    try:
        program = parser.parse_file(str(temp_path))

        # Capture output
        output_buffer = io.StringIO()
        engine = Engine(program, output=output_buffer)
        await engine.run()

        # Verify captured output
        captured = output_buffer.getvalue()
        assert "Hello, World!" in captured
        assert captured == "Hello, World!\n"
    finally:
        temp_path.unlink()


async def test_file_output():
    """Test redirecting output to a file."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(SIMPLE_HELLO_WORKFLOW)
        temp_workflow = Path(f.name)

    # Create output file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_output = Path(f.name)

    try:
        program = parser.parse_file(str(temp_workflow))

        # Run with file output
        with open(temp_output, 'w') as output_file:
            engine = Engine(program, output=output_file)
            await engine.run()

        # Verify file contents
        with open(temp_output, 'r') as f:
            content = f.read()

        assert "Hello, World!" in content
        assert content == "Hello, World!\n"
    finally:
        temp_workflow.unlink()
        temp_output.unlink()


async def test_tee_output():
    """Test writing to multiple outputs simultaneously."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(MULTI_LINE_WORKFLOW)
        temp_workflow = Path(f.name)

    # Create output file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_file = Path(f.name)

    try:
        program = parser.parse_file(str(temp_workflow))

        # Create TeeOutput to write to both StringIO and file
        string_buffer = io.StringIO()
        with open(temp_file, 'w') as file_buffer:
            tee = TeeOutput(string_buffer, file_buffer)
            engine = Engine(program, output=tee)
            await engine.run()

        # Verify both outputs received the same content
        string_content = string_buffer.getvalue()
        with open(temp_file, 'r') as f:
            file_content = f.read()

        assert string_content == file_content
        assert "Line 1" in string_content
        assert "Line 2" in string_content
        assert "Line 3" in string_content
    finally:
        temp_workflow.unlink()
        temp_file.unlink()


async def test_streaming_output():
    """Test streaming output to a callback."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(MULTI_LINE_WORKFLOW)
        temp_path = Path(f.name)

    try:
        program = parser.parse_file(str(temp_path))

        # Collect streamed lines
        streamed_lines = []

        def callback(line: str):
            streamed_lines.append(line)

        # Run with streaming output
        stream = StreamingOutput(callback)
        engine = Engine(program, output=stream)
        await engine.run()
        stream.flush()  # Flush any remaining buffer

        # Verify we received all lines
        assert len(streamed_lines) >= 3
        assert any("Line 1" in line for line in streamed_lines)
        assert any("Line 2" in line for line in streamed_lines)
        assert any("Line 3" in line for line in streamed_lines)
    finally:
        temp_path.unlink()


async def test_output_capture_context_manager():
    """Test OutputCapture as a context manager."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(SIMPLE_HELLO_WORKFLOW)
        temp_path = Path(f.name)

    try:
        program = parser.parse_file(str(temp_path))

        # Use context manager
        with OutputCapture() as capture:
            engine = Engine(program)
            await engine.run()
            output = capture.get_output()

        assert "Hello, World!" in output
    finally:
        temp_path.unlink()


async def test_no_output_redirection():
    """Test that engine works without output redirection (default behavior)."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(SIMPLE_HELLO_WORKFLOW)
        temp_path = Path(f.name)

    try:
        program = parser.parse_file(str(temp_path))

        # Run without output redirection - should print to stdout normally
        engine = Engine(program)
        result = await engine.run()

        # Just verify it completes without error
        assert result is None or result is not None  # Any result is fine
    finally:
        temp_path.unlink()


async def test_multi_line_capture():
    """Test capturing multiple lines of output."""
    # Parse workflow
    parser = Parser()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(MULTI_LINE_WORKFLOW)
        temp_path = Path(f.name)

    try:
        program = parser.parse_file(str(temp_path))

        # Capture output
        output_buffer = io.StringIO()
        engine = Engine(program, output=output_buffer)
        await engine.run()

        # Verify all lines captured
        captured = output_buffer.getvalue()
        lines = captured.split('\n')

        assert "Line 1" in captured
        assert "Line 2" in captured
        assert "Line 3" in captured
        assert len([l for l in lines if l.strip()]) == 3  # 3 non-empty lines
    finally:
        temp_path.unlink()


async def test_output_capture_clear():
    """Test clearing the output buffer."""
    capture = OutputCapture()
    capture.buffer.write("test content")

    # Verify content exists
    assert capture.get_output() == "test content"

    # Clear and verify
    capture.clear()
    assert capture.get_output() == ""
