# AI Chat Examples

This directory contains examples demonstrating how to build AI-powered chat applications using LexFlow's chat history management opcodes combined with pydantic-ai integration.

## Available Examples

### chat_demo.yaml

A non-interactive demo that shows how the chat history opcodes work. It simulates a multi-turn conversation with hardcoded messages to demonstrate:

- Creating a chat history with `chat_create`
- Adding messages with `chat_add_user` and `chat_add_assistant`
- Retrieving message count with `chat_length`
- Getting the last message with `chat_get_last`
- Formatting for display with `chat_format_for_display`
- Converting to AI prompt format with `chat_to_prompt`

**No special requirements** - runs with the base LexFlow installation.

```bash
lexflow examples/integrations/ai_chat/chat_demo.yaml
```

### simple_chat.yaml

An interactive AI chat application that demonstrates:

- Creating a Vertex AI model and agent
- Managing conversation history across multiple turns
- Using `chat_with_agent` to send messages with context
- Displaying formatted chat history at the end

**Requirements:**

```bash
# Install AI dependencies
pip install lexflow[ai]

# Authenticate with Google Cloud
gcloud auth application-default login
```

**Run:**

```bash
lexflow examples/integrations/ai_chat/simple_chat.yaml --input project=YOUR_GCP_PROJECT
```

Replace `YOUR_GCP_PROJECT` with your Google Cloud project ID.

Type your messages and press Enter. Type `quit` to exit and see the full conversation history.

## Chat Opcodes Reference

| Opcode | Description |
|--------|-------------|
| `chat_create()` | Create an empty chat history list |
| `chat_add_user(history, content)` | Add a user message to history |
| `chat_add_assistant(history, content)` | Add an assistant message to history |
| `chat_add_message(history, role, content)` | Add a message with specified role |
| `chat_get_last(history, role?)` | Get the last message (optionally filtered by role) |
| `chat_length(history)` | Get the number of messages |
| `chat_clear(history)` | Clear all messages from history |
| `chat_format_for_display(history)` | Format history as readable text |
| `chat_to_prompt(history)` | Convert history to AI prompt format |
| `chat_with_agent(agent, history, message)` | Send message to AI with history context |

## Chat History Format

Chat history is a list of message dictionaries:

```python
[
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there! How can I help?"},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."}
]
```

## Related Examples

- `examples/integrations/pydantic_ai/vertex_ai_example.yaml` - Basic AI integration without chat history
- `docs/OPCODE_REFERENCE.md` - Full opcode documentation
