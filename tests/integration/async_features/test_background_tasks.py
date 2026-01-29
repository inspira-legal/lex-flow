"""Integration tests for background tasks (Spawn)."""

import io
import pytest
import yaml

from lexflow import Parser, Engine


pytestmark = pytest.mark.asyncio


SPAWN_BASIC_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      counter: 0
      task_started: false
    nodes:
      start:
        opcode: workflow_start
        next: spawn_task
        inputs: {}

      spawn_task:
        opcode: control_spawn
        next: wait_a_bit
        inputs:
          VAR: { literal: "my_task" }
          BODY: { branch: background_work }

      background_work:
        opcode: data_set_variable_to
        next: bg_increment
        inputs:
          VARIABLE: { literal: "task_started" }
          VALUE: { literal: true }

      bg_increment:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "counter" }
          VALUE: { node: add_to_counter }

      add_to_counter:
        opcode: operator_add
        inputs:
          A: { variable: counter }
          B: { literal: 10 }

      wait_a_bit:
        opcode: task_sleep
        next: check_task
        inputs:
          SECONDS: { literal: 0.05 }

      check_task:
        opcode: data_set_variable_to
        next: return_result
        inputs:
          VARIABLE: { literal: "result" }
          VALUE: { node: check_done }

      check_done:
        opcode: task_is_done
        inputs:
          TASK: { variable: my_task }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: counter }
"""


async def test_spawn_basic():
    """Test basic spawn functionality."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(SPAWN_BASIC_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    # Background task should have incremented counter
    assert result == 10


SPAWN_VARIABLE_SHARING_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      shared_value: "initial"
    nodes:
      start:
        opcode: workflow_start
        next: spawn_task
        inputs: {}

      spawn_task:
        opcode: control_spawn
        next: wait
        inputs:
          BODY: { branch: update_shared }

      update_shared:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "shared_value" }
          VALUE: { literal: "updated_by_task" }

      wait:
        opcode: task_sleep
        next: return_value
        inputs:
          SECONDS: { literal: 0.05 }

      return_value:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: shared_value }
"""


async def test_spawn_variable_sharing():
    """Test that spawned tasks share variables with parent scope."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(SPAWN_VARIABLE_SHARING_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    # Task should have modified the shared variable
    assert result == "updated_by_task"


SPAWN_AWAIT_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      result: 0
    nodes:
      start:
        opcode: workflow_start
        next: spawn_task
        inputs: {}

      spawn_task:
        opcode: control_spawn
        next: await_task
        inputs:
          VAR: { literal: "my_task" }
          BODY: { branch: compute_value }

      compute_value:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "result" }
          VALUE: { literal: 42 }

      await_task:
        opcode: task_await
        next: return_result
        inputs:
          TASK: { variable: my_task }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: result }
"""


async def test_spawn_await():
    """Test awaiting a spawned task."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(SPAWN_AWAIT_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert result == 42
