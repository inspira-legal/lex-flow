"""Integration tests for AsyncForEach."""

import pytest
import yaml

from lexflow import Parser, Engine


pytestmark = pytest.mark.asyncio


ASYNC_FOREACH_BASIC_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      total: 0
      items: [1, 2, 3, 4, 5]
    nodes:
      start:
        opcode: workflow_start
        next: async_loop
        inputs: {}

      async_loop:
        opcode: control_async_foreach
        next: return_result
        inputs:
          VAR: { literal: "item" }
          ITERABLE: { variable: items }
          BODY: { branch: add_item }

      add_item:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "total" }
          VALUE: { node: sum_op }

      sum_op:
        opcode: operator_add
        inputs:
          A: { variable: total }
          B: { variable: item }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: total }
"""


async def test_async_foreach_basic():
    """Test async foreach with regular list (falls back to sync iteration)."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(ASYNC_FOREACH_BASIC_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert result == 15  # 1 + 2 + 3 + 4 + 5


ASYNC_FOREACH_DICT_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      keys: []
      data:
        name: Alice
        age: 30
        city: NYC
    nodes:
      start:
        opcode: workflow_start
        next: async_loop
        inputs: {}

      async_loop:
        opcode: control_async_foreach
        next: return_result
        inputs:
          VAR: { literal: "key" }
          ITERABLE: { variable: data }
          BODY: { branch: collect_key }

      collect_key:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "keys" }
          VALUE: { node: append_key }

      append_key:
        opcode: list_append
        inputs:
          LIST: { variable: keys }
          VALUE: { variable: key }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: keys }
"""


async def test_async_foreach_dict():
    """Test async foreach over dictionary keys."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(ASYNC_FOREACH_DICT_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert set(result) == {"name", "age", "city"}


ASYNC_FOREACH_BREAK_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      total: 0
      items: [1, 2, 3, 4, 5]
    nodes:
      start:
        opcode: workflow_start
        next: async_loop
        inputs: {}

      async_loop:
        opcode: control_async_foreach
        next: return_result
        inputs:
          VAR: { literal: "item" }
          ITERABLE: { variable: items }
          BODY: { branch: check_and_add }

      check_and_add:
        opcode: control_if
        next: null
        inputs:
          CONDITION: { node: check_gt_3 }
          THEN: { branch: do_nothing }

      check_gt_3:
        opcode: operator_greater_than
        inputs:
          A: { variable: item }
          B: { literal: 3 }

      do_nothing:
        opcode: noop
        next: null
        inputs: {}

      add_item:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "total" }
          VALUE: { node: sum_op }

      sum_op:
        opcode: operator_add
        inputs:
          A: { variable: total }
          B: { variable: item }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: total }
"""
