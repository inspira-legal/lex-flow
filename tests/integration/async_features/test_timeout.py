"""Integration tests for Timeout functionality."""

import asyncio
import pytest
import yaml

from lexflow import Parser, Engine


pytestmark = pytest.mark.asyncio


TIMEOUT_COMPLETES_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      result: "not set"
    nodes:
      start:
        opcode: workflow_start
        next: with_timeout
        inputs: {}

      with_timeout:
        opcode: async_timeout
        next: return_result
        inputs:
          TIMEOUT: { literal: 5.0 }
          BODY: { branch: fast_work }

      fast_work:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "result" }
          VALUE: { literal: "completed" }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: result }
"""


async def test_timeout_completes():
    """Test timeout when body completes in time."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(TIMEOUT_COMPLETES_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert result == "completed"


TIMEOUT_FALLBACK_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      result: "not set"
    nodes:
      start:
        opcode: workflow_start
        next: with_timeout
        inputs: {}

      with_timeout:
        opcode: async_timeout
        next: return_result
        inputs:
          TIMEOUT: { literal: 0.01 }
          BODY: { branch: slow_work }
          ON_TIMEOUT: { branch: fallback }

      slow_work:
        opcode: task_sleep
        next: set_result
        inputs:
          SECONDS: { literal: 10.0 }

      set_result:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "result" }
          VALUE: { literal: "completed" }

      fallback:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "result" }
          VALUE: { literal: "timed out" }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: result }
"""


async def test_timeout_fallback():
    """Test timeout fallback when body exceeds time limit."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(TIMEOUT_FALLBACK_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert result == "timed out"


TIMEOUT_RAISES_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      result: "not set"
    nodes:
      start:
        opcode: workflow_start
        next: with_timeout
        inputs: {}

      with_timeout:
        opcode: async_timeout
        next: return_result
        inputs:
          TIMEOUT: { literal: 0.01 }
          BODY: { branch: slow_work }

      slow_work:
        opcode: task_sleep
        next: null
        inputs:
          SECONDS: { literal: 10.0 }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: result }
"""


async def test_timeout_raises():
    """Test that timeout raises TimeoutError when no fallback provided."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(TIMEOUT_RAISES_WORKFLOW))

    engine = Engine(program)

    with pytest.raises(asyncio.TimeoutError):
        await engine.run()
