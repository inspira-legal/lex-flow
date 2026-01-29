"""Integration tests for Channel-based Fork communication."""

import pytest
import yaml

from lexflow import Parser, Engine


pytestmark = pytest.mark.asyncio


CHANNEL_FORK_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      result: 0
      channel: null
    nodes:
      start:
        opcode: workflow_start
        next: create_channel
        inputs: {}

      create_channel:
        opcode: data_set_variable_to
        next: fork_branches
        inputs:
          VARIABLE: { literal: "channel" }
          VALUE: { node: make_channel }

      make_channel:
        opcode: channel_create
        inputs:
          SIZE: { literal: 10 }

      fork_branches:
        opcode: control_fork
        next: receive_result
        inputs:
          BRANCH1: { branch: producer }
          BRANCH2: { branch: consumer }

      producer:
        opcode: channel_send
        next: null
        inputs:
          CHANNEL: { variable: channel }
          VALUE: { literal: 42 }

      consumer:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "result" }
          VALUE: { node: receive_value }

      receive_value:
        opcode: channel_receive
        inputs:
          CHANNEL: { variable: channel }

      receive_result:
        opcode: noop
        next: return_result
        inputs: {}

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: result }
"""


async def test_channel_fork_communication():
    """Test that Fork branches can communicate via channels."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(CHANNEL_FORK_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert result == 42


CHANNEL_MULTIPLE_VALUES_WORKFLOW = """
workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables:
      total: 0
      channel: null
    nodes:
      start:
        opcode: workflow_start
        next: create_channel
        inputs: {}

      create_channel:
        opcode: data_set_variable_to
        next: fork_branches
        inputs:
          VARIABLE: { literal: "channel" }
          VALUE: { node: make_channel }

      make_channel:
        opcode: channel_create
        inputs:
          SIZE: { literal: 10 }

      fork_branches:
        opcode: control_fork
        next: return_result
        inputs:
          BRANCH1: { branch: producer }
          BRANCH2: { branch: consumer }

      producer:
        opcode: channel_send
        next: send2
        inputs:
          CHANNEL: { variable: channel }
          VALUE: { literal: 10 }

      send2:
        opcode: channel_send
        next: send3
        inputs:
          CHANNEL: { variable: channel }
          VALUE: { literal: 20 }

      send3:
        opcode: channel_send
        next: close_ch
        inputs:
          CHANNEL: { variable: channel }
          VALUE: { literal: 30 }

      close_ch:
        opcode: channel_close
        next: null
        inputs:
          CHANNEL: { variable: channel }

      consumer:
        opcode: data_set_variable_to
        next: recv2
        inputs:
          VARIABLE: { literal: "total" }
          VALUE: { node: recv1 }

      recv1:
        opcode: channel_receive
        inputs:
          CHANNEL: { variable: channel }

      recv2:
        opcode: data_set_variable_to
        next: recv3
        inputs:
          VARIABLE: { literal: "total" }
          VALUE: { node: add_recv2 }

      add_recv2:
        opcode: operator_add
        inputs:
          A: { variable: total }
          B: { node: recv2_val }

      recv2_val:
        opcode: channel_receive
        inputs:
          CHANNEL: { variable: channel }

      recv3:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE: { literal: "total" }
          VALUE: { node: add_recv3 }

      add_recv3:
        opcode: operator_add
        inputs:
          A: { variable: total }
          B: { node: recv3_val }

      recv3_val:
        opcode: channel_receive
        inputs:
          CHANNEL: { variable: channel }

      return_result:
        opcode: workflow_return
        next: null
        inputs:
          VALUE: { variable: total }
"""


async def test_channel_multiple_values():
    """Test sending and receiving multiple values through a channel."""
    parser = Parser()
    program = parser.parse_dict(yaml.safe_load(CHANNEL_MULTIPLE_VALUES_WORKFLOW))

    engine = Engine(program)
    result = await engine.run()

    assert result == 60  # 10 + 20 + 30
