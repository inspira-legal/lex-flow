"""Chat history management opcodes for LexFlow.

This module provides opcodes for managing conversational AI chat histories.
No external dependencies - pure Python list/dict manipulation.

Chat History Format:
    [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
    ]
"""

from typing import Any, List, Optional

from .opcodes import opcode, register_category

# Register category at module load time (no external deps)
register_category(
    id="chat",
    label="Chat Operations",
    prefix="chat_",
    color="#6366F1",
    icon="💬",
    order=240,
)


@opcode(category="chat")
async def chat_create() -> List[dict]:
    """Create a new empty chat history.

    Returns:
        Empty list ready to store chat messages
    """
    return []


@opcode(category="chat")
async def chat_add_message(history: List[dict], role: str, content: str) -> List[dict]:
    """Add a message to chat history.

    Args:
        history: The chat history list to modify
        role: Message role - "user" or "assistant"
        content: The message content

    Returns:
        The updated history (same list, modified in place)

    Raises:
        ValueError: If role is not "user" or "assistant"
    """
    if role not in ("user", "assistant"):
        raise ValueError(f"Invalid role '{role}'. Must be 'user' or 'assistant'.")
    history.append({"role": role, "content": content})
    return history


@opcode(category="chat")
async def chat_add_user(history: List[dict], content: str) -> List[dict]:
    """Add a user message to chat history.

    Args:
        history: The chat history list to modify
        content: The user's message

    Returns:
        The updated history
    """
    history.append({"role": "user", "content": content})
    return history


@opcode(category="chat")
async def chat_add_assistant(history: List[dict], content: str) -> List[dict]:
    """Add an assistant message to chat history.

    Args:
        history: The chat history list to modify
        content: The assistant's response

    Returns:
        The updated history
    """
    history.append({"role": "assistant", "content": content})
    return history


@opcode(category="chat")
async def chat_get_last(
    history: List[dict], role: Optional[str] = None
) -> Optional[dict]:
    """Get the last message from chat history.

    Args:
        history: The chat history list
        role: Optional filter - get last message with this role

    Returns:
        The last message dict, or None if empty or no match
    """
    if not history:
        return None

    if role is None:
        return history[-1]

    for message in reversed(history):
        if message.get("role") == role:
            return message

    return None


@opcode(category="chat")
async def chat_length(history: List[dict]) -> int:
    """Get the number of messages in chat history.

    Args:
        history: The chat history list

    Returns:
        Number of messages
    """
    return len(history)


@opcode(category="chat")
async def chat_clear(history: List[dict]) -> List[dict]:
    """Clear all messages from chat history.

    Args:
        history: The chat history list to clear

    Returns:
        The same list, now empty
    """
    history.clear()
    return history


@opcode(category="chat")
async def chat_format_for_display(history: List[dict]) -> str:
    """Format chat history as a readable string.

    Args:
        history: The chat history list

    Returns:
        Formatted string with each message on its own line
    """
    if not history:
        return "(empty chat)"

    lines = []
    for message in history:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        lines.append(f"{role.capitalize()}: {content}")

    return "\n".join(lines)


@opcode(category="chat")
async def chat_to_prompt(history: List[dict]) -> str:
    """Convert chat history to a single prompt string for AI.

    Args:
        history: The chat history list

    Returns:
        A formatted string containing the conversation context
    """
    if not history:
        return ""

    lines = ["Previous conversation:"]
    for message in history:
        role = message.get("role", "unknown").capitalize()
        content = message.get("content", "")
        lines.append(f"{role}: {content}")

    lines.append("")
    lines.append("Continue the conversation.")

    return "\n".join(lines)


@opcode(category="chat")
async def chat_with_agent(agent: Any, history: List[dict], user_message: str) -> str:
    """Send a message to an AI agent with conversation history context.

    This opcode:
    1. Adds the user message to history
    2. Builds a context-aware prompt from history
    3. Sends to the agent
    4. Adds the response to history
    5. Returns the response

    Args:
        agent: A pydantic-ai Agent instance
        history: The chat history list (will be modified)
        user_message: The new user message to send

    Returns:
        The assistant's response string
    """
    history.append({"role": "user", "content": user_message})

    if len(history) == 1:
        prompt = user_message
    else:
        context_lines = []
        for message in history[:-1]:
            role = message.get("role", "unknown").capitalize()
            content = message.get("content", "")
            context_lines.append(f"{role}: {content}")

        prompt = (
            "Previous conversation:\n"
            + "\n".join(context_lines)
            + f"\n\nUser: {user_message}\n\n"
            + "Respond to the user's latest message, taking into account the conversation history."
        )

    result = await agent.run(prompt)
    response = result.output

    history.append({"role": "assistant", "content": response})

    return response
