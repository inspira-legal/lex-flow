"""Pydantic AI bindings for LexFlow.

This module provides opcodes for using pydantic_ai agents with Google Vertex AI.

Installation:
    pip install lexflow[ai]

Authentication:
    Vertex AI requires Google Cloud authentication:
    - gcloud auth application-default login
    - Or set GOOGLE_APPLICATION_CREDENTIALS environment variable
"""

from typing import Any, Callable, List, Optional, Union
from contextvars import ContextVar
import asyncio
import inspect

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider

    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False


# Context var for tracking thread-safe tool calls
_tool_call_context: ContextVar[dict] = ContextVar("tool_call_context", default=None)


def _check_availability():
    """Check if pydantic_ai is available and raise helpful error if not."""
    if not PYDANTIC_AI_AVAILABLE:
        raise ImportError(
            "pydantic-ai is not installed. Install it with:\n"
            "  pip install lexflow[ai]\n"
            "or:\n"
            "  pip install 'pydantic-ai-slim[google]'"
        )


def _normalize_messages(messages: Union[str, List[dict]]) -> List[dict]:
    """Normalize messages to list format.

    Args:
        messages: String (user prompt) or list of {role, content}

    Returns:
        List of dicts with role and content
    """
    if isinstance(messages, str):
        return [{"role": "user", "content": messages}]
    return messages


def _format_messages_for_prompt(messages: List[dict]) -> str:
    """Format message history as prompt string.

    Args:
        messages: List of {role, content}

    Returns:
        Formatted string for the agent
    """
    lines = []
    for msg in messages:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _validate_tools_exist(tools: List[str], registry) -> None:
    """Validate that all tools exist in the registry.

    Args:
        tools: List of opcode names
        registry: OpcodeRegistry instance

    Raises:
        ValueError: If any tool doesn't exist
    """
    available = set(registry.list_opcodes())
    missing = set(tools) - available
    if missing:
        raise ValueError(f"Tools not found in registry: {missing}")


def _create_output_model(output_schema: Optional[dict]):
    """Create Pydantic model from output schema.

    Args:
        output_schema: Dict with {text: "string", data: {...}} or None

    Returns:
        Pydantic model class or None
    """
    if not output_schema:
        return None

    from pydantic import create_model

    type_mapping = {
        "string": str,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "object": dict,
        "dict": dict,
        "list": list,
        "array": list,
    }

    # If data schema specified, create typed model
    data_schema = output_schema.get("data")
    if data_schema and isinstance(data_schema, dict):
        fields = {}
        for name, type_str in data_schema.items():
            py_type = type_mapping.get(str(type_str).lower(), Any)
            fields[name] = (py_type, ...)
        DataModel = create_model("DataModel", **fields)
        return create_model("OutputModel", text=(str, ...), data=(DataModel, ...))

    # Simple case: just text
    return create_model("OutputModel", text=(str, ...), data=(Any, None))


def _create_tool_wrapper(
    opcode_name: str,
    registry,
    allowlist: set
) -> Callable:
    """Create tool wrapper that converts kwargs -> positional args.

    PydanticAI calls tools with kwargs (JSON object).
    registry.call() expects positional args (list).
    This wrapper does the conversion using get_interface().

    The wrapper is given a proper __signature__ so PydanticAI can
    introspect the expected parameters and tell the LLM about them.

    Args:
        opcode_name: Name of the opcode
        registry: OpcodeRegistry instance
        allowlist: Set of allowed opcodes

    Returns:
        Async function usable as a tool
    """
    interface = registry.get_interface(opcode_name)
    params_info = interface.get("parameters", [])

    async def tool_wrapper(**kwargs) -> Any:
        # Check tracking context (max_tool_calls)
        ctx = _tool_call_context.get()
        if ctx:
            # Verify allowlist (extra security)
            if opcode_name not in ctx["allowlist"]:
                raise PermissionError(f"Tool '{opcode_name}' not in allowlist")

            # Increment counter
            ctx["count"] += 1
            if ctx["count"] > ctx["max"]:
                raise RuntimeError(f"Maximum tool calls ({ctx['max']}) exceeded")

        # Map kwargs to positional list based on parameter order
        args_list = []
        for param in params_info:
            param_name = param["name"]
            if param_name in kwargs:
                args_list.append(kwargs[param_name])
            elif not param.get("required", True):
                args_list.append(param.get("default"))
            else:
                raise ValueError(
                    f"Missing required parameter '{param_name}' for tool '{opcode_name}'"
                )

        # Execute opcode via registry
        return await registry.call(opcode_name, args_list)

    # Build proper signature for PydanticAI to introspect
    # This tells the LLM what parameters the tool expects
    sig_params = []
    for p in params_info:
        default = inspect.Parameter.empty
        if not p.get("required", True):
            default = p.get("default", None)

        sig_params.append(
            inspect.Parameter(
                p["name"],
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=Any,
            )
        )

    tool_wrapper.__signature__ = inspect.Signature(sig_params)
    tool_wrapper.__name__ = opcode_name
    tool_wrapper.__doc__ = interface.get("doc", f"Execute {opcode_name} opcode")

    # Set __annotations__ for get_type_hints() used by pydantic_ai
    tool_wrapper.__annotations__ = {p["name"]: Any for p in params_info}
    tool_wrapper.__annotations__["return"] = Any

    return tool_wrapper


def register_pydantic_ai_opcodes():
    """Register pydantic_ai opcodes to the default registry."""
    if not PYDANTIC_AI_AVAILABLE:
        return

    from .opcodes import default_registry

    @default_registry.register()
    async def pydantic_ai_create_vertex_model(
        model_name: str, project: Optional[str] = None, location: Optional[str] = None
    ) -> Any:
        """Create a Google Vertex AI model instance.

        Args:
            model_name: Name of the model (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
            project: Optional GCP project ID (uses default if not specified)
            location: Optional region (e.g., "us-central1", "asia-east1")

        Returns:
            GoogleModel instance configured for Vertex AI

        Example:
            model_name: "gemini-1.5-flash"
            location: "us-central1"

        Authentication:
            Requires Google Cloud authentication via:
            - gcloud auth application-default login
            - Or GOOGLE_APPLICATION_CREDENTIALS environment variable
        """
        _check_availability()

        kwargs = {"vertexai": True}
        if project:
            kwargs["project"] = project
        if location:
            kwargs["location"] = location

        provider = GoogleProvider(**kwargs)
        model = GoogleModel(model_name, provider=provider)
        return model

    @default_registry.register()
    async def pydantic_ai_create_agent(
        model: Any, instructions: str = "", system_prompt: str = ""
    ) -> Any:
        """Create a pydantic_ai Agent.

        Args:
            model: Model instance (from pydantic_ai_create_vertex_model)
            instructions: Optional instructions for the agent
            system_prompt: Optional static system prompt

        Returns:
            Agent instance ready to use

        Example:
            model: { node: vertex_model }
            instructions: "You are a helpful assistant. Be concise."
        """
        _check_availability()

        kwargs = {"model": model}
        if instructions:
            kwargs["instructions"] = instructions
        if system_prompt:
            kwargs["system_prompt"] = system_prompt

        agent = Agent(**kwargs)
        return agent

    @default_registry.register()
    async def pydantic_ai_run_sync(agent: Any, prompt: str) -> str:
        """Run agent with a prompt.

        Args:
            agent: Agent instance (from pydantic_ai_create_agent)
            prompt: User prompt/query to send to the agent

        Returns:
            String output from the agent

        Example:
            agent: { node: my_agent }
            prompt: "What is 2+2?"

        Note:
            Both pydantic_ai_run_sync and pydantic_ai_run work identically
            in LexFlow (both are async). The _sync suffix is kept for
            backward compatibility.
        """
        _check_availability()

        result = await agent.run(prompt)
        return result.output

    @default_registry.register()
    async def pydantic_ai_run(agent: Any, prompt: str) -> str:
        """Run agent asynchronously with a prompt.

        Args:
            agent: Agent instance (from pydantic_ai_create_agent)
            prompt: User prompt/query to send to the agent

        Returns:
            String output from the agent

        Example:
            agent: { node: my_agent }
            prompt: "Explain quantum computing in one sentence."
        """
        _check_availability()

        result = await agent.run(prompt)
        return result.output

    @default_registry.register()
    async def ai_agent_with_tools(
        agent: Any,
        messages: Union[str, List[dict]],
        tools: List[str],
        output: Optional[dict] = None,
        max_tool_calls: int = 10,
        timeout_seconds: float = 300.0,
    ) -> dict:
        """Run an AI agent with access to LexFlow opcodes as tools.

        This opcode enables agentic workflows where the LLM can reason about
        and call LexFlow opcodes to accomplish tasks.

        Args:
            agent: Pre-created agent from pydantic_ai_create_agent
            messages: String prompt or list of {role, content} message dicts.
                     If string, normalizes to [{role: "user", content: <string>}]
            tools: List of opcode names the agent is allowed to call
            output: Optional schema for structured output: {text: "string", data: {...}}
            max_tool_calls: Maximum number of tool calls allowed (default: 10)
            timeout_seconds: Timeout for entire operation in seconds (default: 300)

        Returns:
            Dict with {text: str, data: Any} containing the agent's response

        Raises:
            PermissionError: If agent tries to call a tool not in the allowlist
            ValueError: If tools don't exist or messages format is invalid
            TimeoutError: If execution exceeds timeout_seconds
            RuntimeError: If max_tool_calls exceeded or LLM/tool error occurs

        Example YAML:
            agent_call:
              opcode: ai_agent_with_tools
              isReporter: true
              inputs:
                agent: {variable: "my_agent"}
                messages: {literal: "Calculate 15 * 23"}
                tools:
                  literal:
                    - operator_multiply
                    - operator_add
                max_tool_calls: {literal: 5}
                timeout_seconds: {literal: 30}

        Note:
            This is a reporter opcode (isReporter: true, no next).
            To avoid re-execution, store the result in a variable immediately:

            store_result:
              opcode: data_set_variable_to
              next: ...
              inputs:
                VARIABLE: {literal: "result"}
                VALUE: {node: agent_call}
        """
        _check_availability()

        from pydantic_ai import Agent, Tool

        # 1. Validate that tools exist in the registry
        _validate_tools_exist(tools, default_registry)

        # 2. Normalize messages
        normalized_messages = _normalize_messages(messages)
        prompt = _format_messages_for_prompt(normalized_messages)

        # 3. Create tool wrappers
        allowlist = set(tools)
        tool_objects = []
        for tool_name in tools:
            wrapper = _create_tool_wrapper(tool_name, default_registry, allowlist)
            tool_objects.append(Tool(wrapper, name=tool_name))

        # 4. Create structured output model (if specified)
        result_type = _create_output_model(output)

        # 5. Create new agent with tools
        # PydanticAI requires tools at Agent creation time
        agent_kwargs = {
            "model": agent._model,
            "tools": tool_objects,
        }

        # Preserve instructions from original agent if present
        if hasattr(agent, "_instructions") and agent._instructions:
            agent_kwargs["instructions"] = agent._instructions
        if hasattr(agent, "_system_prompt") and agent._system_prompt:
            agent_kwargs["system_prompt"] = agent._system_prompt

        # Add result_type if output schema provided
        if result_type:
            agent_kwargs["result_type"] = result_type

        agent_with_tools = Agent(**agent_kwargs)

        # 6. Setup tool call tracking context
        ctx = {"count": 0, "max": max_tool_calls, "allowlist": allowlist}
        token = _tool_call_context.set(ctx)

        try:
            # 7. Execute with timeout
            async with asyncio.timeout(timeout_seconds):
                result = await agent_with_tools.run(prompt)

            # 8. Format output
            if result_type and hasattr(result.output, "text"):
                return {
                    "text": result.output.text,
                    "data": getattr(result.output, "data", None),
                }
            else:
                return {
                    "text": str(result.output),
                    "data": None,
                }

        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Agent execution exceeded {timeout_seconds} seconds"
            )
        except (PermissionError, ValueError, RuntimeError):
            # Re-raise known exceptions without wrapping
            raise
        except Exception as e:
            # Wrap other exceptions as RuntimeError
            raise RuntimeError(f"Agent error: {e}") from e
        finally:
            # Clean up context
            _tool_call_context.reset(token)
