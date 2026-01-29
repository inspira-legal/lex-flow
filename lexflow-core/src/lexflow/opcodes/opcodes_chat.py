"""Chat history management opcodes for LexFlow.

This module provides opcodes for managing conversational AI chat histories.
It demonstrates how to create stateful conversation workflows that integrate
with the pydantic-ai opcodes.

No external dependencies - pure Python list/dict manipulation.

Chat History Format:
    [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help?"},
        ...
    ]

Example Usage:
    1. Create a chat history: chat_create()
    2. Add messages: chat_add_user(history, "Hello")
    3. Format for display: chat_format_for_display(history)
    4. Use with AI agent: chat_with_agent(agent, history, "What is 2+2?")
"""

from typing import Any, List, Optional

from .opcodes import opcode


# ============================================================================
# Chat History Management
# ============================================================================


@opcode()
async def chat_create() -> List[dict]:
    """Create a new empty chat history.

    Returns:
        Empty list ready to store chat messages.

    Example:
        history = chat_create()
        # Returns: []
    """
    return []


@opcode()
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

    Example:
        chat_add_message(history, "user", "Hello!")
        chat_add_message(history, "assistant", "Hi there!")
    """
    if role not in ("user", "assistant"):
        raise ValueError(f"Invalid role '{role}'. Must be 'user' or 'assistant'.")

    history.append({"role": role, "content": content})
    return history


@opcode()
async def chat_add_user(history: List[dict], content: str) -> List[dict]:
    """Add a user message to chat history.

    Shorthand for chat_add_message(history, "user", content).

    Args:
        history: The chat history list to modify
        content: The user's message

    Returns:
        The updated history

    Example:
        chat_add_user(history, "What is the weather today?")
    """
    history.append({"role": "user", "content": content})
    return history


@opcode()
async def chat_add_assistant(history: List[dict], content: str) -> List[dict]:
    """Add an assistant message to chat history.

    Shorthand for chat_add_message(history, "assistant", content).

    Args:
        history: The chat history list to modify
        content: The assistant's response

    Returns:
        The updated history

    Example:
        chat_add_assistant(history, "The weather is sunny!")
    """
    history.append({"role": "assistant", "content": content})
    return history


@opcode()
async def chat_get_last(
    history: List[dict], role: Optional[str] = None
) -> Optional[dict]:
    """Get the last message from chat history.

    Args:
        history: The chat history list
        role: Optional filter - if specified, get last message with this role

    Returns:
        The last message dict, or None if history is empty or no matching message

    Example:
        # Get last message of any type
        last = chat_get_last(history)
        # Returns: {"role": "assistant", "content": "..."}

        # Get last user message specifically
        last_user = chat_get_last(history, "user")
    """
    if not history:
        return None

    if role is None:
        return history[-1]

    # Find last message with matching role
    for message in reversed(history):
        if message.get("role") == role:
            return message

    return None


@opcode()
async def chat_length(history: List[dict]) -> int:
    """Get the number of messages in chat history.

    Args:
        history: The chat history list

    Returns:
        Number of messages

    Example:
        count = chat_length(history)  # Returns: 5
    """
    return len(history)


@opcode()
async def chat_clear(history: List[dict]) -> List[dict]:
    """Clear all messages from chat history.

    Args:
        history: The chat history list to clear

    Returns:
        The same list, now empty

    Example:
        chat_clear(history)
        # history is now []
    """
    history.clear()
    return history


# ============================================================================
# Formatting
# ============================================================================


@opcode()
async def chat_format_for_display(history: List[dict]) -> str:
    """Format chat history as a readable string for display.

    Args:
        history: The chat history list

    Returns:
        Formatted string with each message on its own line(s)

    Example:
        Output:
        User: Hello!
        Assistant: Hi there! How can I help you today?
        User: What is 2+2?
        Assistant: 2+2 equals 4.
    """
    if not history:
        return "(empty chat)"

    lines = []
    for message in history:
        role = message.get("role", "unknown")
        content = message.get("content", "")

        # Capitalize role for display
        display_role = role.capitalize()
        lines.append(f"{display_role}: {content}")

    return "\n".join(lines)


@opcode()
async def chat_to_prompt(history: List[dict]) -> str:
    """Convert chat history to a single prompt string for AI.

    This formats the conversation history in a way that can be passed
    as context to an AI agent that doesn't natively support chat history.

    Args:
        history: The chat history list

    Returns:
        A formatted string containing the conversation context

    Example:
        prompt = chat_to_prompt(history)
        # Returns:
        # "Previous conversation:
        # User: Hello!
        # Assistant: Hi there!
        #
        # Continue the conversation."
    """
    if not history:
        return ""

    lines = ["Previous conversation:"]
    for message in history:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        display_role = role.capitalize()
        lines.append(f"{display_role}: {content}")

    lines.append("")
    lines.append("Continue the conversation.")

    return "\n".join(lines)


# ============================================================================
# Integration with pydantic-ai
# ============================================================================


@opcode()
async def chat_with_agent(agent: Any, history: List[dict], user_message: str) -> str:
    """Send a message to an AI agent with conversation history context.

    This opcode:
    1. Adds the user message to history
    2. Builds a context-aware prompt from history
    3. Sends to the agent
    4. Adds the response to history
    5. Returns the response

    Args:
        agent: A pydantic-ai Agent instance (from pydantic_ai_create_agent)
        history: The chat history list (will be modified)
        user_message: The new user message to send

    Returns:
        The assistant's response string

    Example:
        response = chat_with_agent(agent, history, "What is the capital of France?")
        # history now contains both the user message and assistant response
        # response = "The capital of France is Paris."

    Note:
        The agent must be created using pydantic_ai_create_agent opcode.
        This opcode modifies the history in place.
    """
    # Add user message to history
    history.append({"role": "user", "content": user_message})

    # Build context-aware prompt
    if len(history) == 1:
        # First message, no context needed
        prompt = user_message
    else:
        # Build context from previous messages (excluding the one we just added)
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

    # Call the agent
    result = await agent.run(prompt)
    response = result.output

    # Add assistant response to history
    history.append({"role": "assistant", "content": response})

    return response
