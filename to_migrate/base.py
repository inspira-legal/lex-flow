from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import structlog
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_ai.exceptions import (
    AgentRunError,
    UnexpectedModelBehavior,
    UsageLimitExceeded,
)
from pydantic_graph import BaseNode, Graph
from pydantic_graph.exceptions import GraphRuntimeError

from app.ai.exceptions import (
    ActionConfigurationError,
    ActionInputError,
    ModelExecutionError,
    OutputParsingError,
    ResourceLimitError,
    SafetyError,
    WorkflowExecutionError,
)

logger = structlog.get_logger(__name__)

T = TypeVar("T")
ActionType = TypeVar("ActionType", bound="Action")


class ActionRegistry:
    _actions: Dict[str, Type["Action"]] = {}

    @classmethod
    def register(cls, action_cls: Type["Action"]) -> Type["Action"]:
        name = getattr(action_cls, "name", None)
        if name is None:
            raise NotImplementedError(
                f"{action_cls} must have a 'name' class attribute"
            )

        cls._actions[name] = action_cls
        return action_cls

    @classmethod
    def get(cls, name: str) -> Type["Action"]:
        if name not in cls._actions:
            raise KeyError(f"Action '{name}' not found in registry")
        return cls._actions[name]

    @classmethod
    def items(cls) -> List[str]:
        return cls._actions.items()

    @classmethod
    def all(cls) -> Dict[str, Type["Action"]]:
        return cls._actions.copy()


class Blob(BaseModel):
    file_name: Optional[str]
    content_type: str
    data: bytes
    pages: int | None = Field(default=None, ge=0)


class ActionInput(BaseModel):
    documents: Union[List[Blob], Blob]
    parameters: Dict[str, Any] = Field(default_factory=dict)

    def get_document(self) -> Blob:
        """Helper to get the first document or the document itself if single."""
        if isinstance(self.documents, list):
            if not self.documents:
                raise ActionInputError("No documents provided")
            return self.documents[0]
        return self.documents


class ActionOutput(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    answer: Optional[Any] = None


class Action(ABC):
    """Base Action abstract class."""

    allow_multiple_docs: bool = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the action."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the action."""

    @abstractmethod
    async def run(self, input: ActionInput) -> ActionOutput:
        """
        Action entrypoint.
        Should return ActionOutput on success or raise an ActionBaseException on failure.
        """

    def __init_subclass__(cls, **kwargs):
        """
        Register actions when subclassing.
        Uses the ActionRegistry rather than managing registration internally.
        """
        if kwargs.get("base", False):
            return

        ActionRegistry.register(cls)


class SimpleAction(Action, base=True):
    """Base class to define stateless actions using a Pydantic AI Agent."""

    @property
    @abstractmethod
    def agent(self):
        """Pydantic AI agent"""

    async def run(self, input: ActionInput) -> ActionOutput:
        """Runs the agent and returns the output, raising ModelExecutionError on failure."""
        try:
            content = await self.agent.run(input.documents)
            return ActionOutput(answer=content.data)
        except AgentRunError as e:
            logger.warning("SimpleAction failed", action=self.name, error=str(e))
            raise ModelExecutionError(
                original_exception=e, action_name=self.name
            ) from e
        except Exception as e:
            logger.error(
                "SimpleAction failed", action=self.name, error=str(e), exc_info=True
            )
            raise ModelExecutionError(
                f"Unexpected agent error: {str(e)}",
                original_exception=e,
                action_name=self.name,
            ) from e


class BaseWorkflowState(BaseModel):
    """Base state model for workflow actions."""

    metadata: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    documents: List[Blob] = Field(default_factory=list)

    @model_validator(mode="after")
    def populate_metadata(self) -> "BaseWorkflowState":
        """Populate metadata from fields with include_in_metadata=True."""
        if self.metadata is None:
            self.metadata = {}

        for field_name, field_info in self.model_fields.items():
            if field_name == "metadata":
                continue

            include_in_meta = False
            schema_extra = field_info.json_schema_extra

            if isinstance(schema_extra, dict):
                include_in_meta = schema_extra.get("include_in_metadata") is True
            elif callable(schema_extra):
                try:
                    extra_dict = schema_extra(None)
                    if isinstance(extra_dict, dict):
                        include_in_meta = extra_dict.get("include_in_metadata") is True
                except Exception as e:
                    logger.warning(
                        "Error calling schema_extra",
                        field_name=field_name,
                        error=str(e),
                    )
                    raise WorkflowExecutionError(
                        message="Failed to populate metadata"
                    ) from e

            if include_in_meta and hasattr(self, field_name):
                self.metadata[field_name] = getattr(self, field_name)

        return self

    model_config = ConfigDict(arbitrary_types_allowed=True)


class GraphAction(Action, base=True):
    """Base class for graph workflows using Pydantic Graph."""

    @property
    @abstractmethod
    def state_class(self) -> Type[BaseWorkflowState]:
        """Pydantic model for workflow state."""

    @property
    @abstractmethod
    def start_node(self) -> Type[BaseNode]:
        """First node class of the graph."""

    @property
    @abstractmethod
    def graph(self) -> Graph:
        """Pydantic graph instance."""

    async def run(self, input: ActionInput) -> ActionOutput:
        """Runs the graph workflow, returning the final output or raising appropriate exceptions."""
        state = self.state_class(documents=input.documents, **input.parameters)

        try:
            start_node_instance = self.start_node()
            end = await self.graph.run(start_node_instance, state=state)

            if end.state:
                end.state.populate_metadata()
                metadata = end.state.metadata
            else:
                metadata = {}

            return ActionOutput(metadata=metadata, answer=end.output)

        except (
            ModelExecutionError,
            OutputParsingError,
            ResourceLimitError,
            ActionInputError,
            ActionConfigurationError,
        ) as e:
            logger.warning(
                f"GraphAction failed: {type(e).__name__}",
                action=self.name,
                error_code=getattr(e, "error_code", None),
                error=str(e),
            )
            raise e
        except UsageLimitExceeded as e:
            raise ResourceLimitError() from e
        except UnexpectedModelBehavior as e:
            raise SafetyError() from e
        except AgentRunError as e:
            logger.error(
                "GraphAction failed: Uncaught AgentRunError",
                action=self.name,
                error=str(e),
            )
            raise ModelExecutionError(
                original_exception=e,
                action_name=self.name,
                current_state=state.model_dump(),
            ) from e
        except GraphRuntimeError as e:
            logger.error(
                "GraphAction failed: GraphRunError",
                action=self.name,
                error=str(e),
            )
            state_data = getattr(e, "state", state).model_dump()
            raise WorkflowExecutionError(
                partial_state=state_data, original_exception=e, action_name=self.name
            ) from e
        except Exception as e:
            logger.error(
                "GraphAction failed: Unexpected error",
                action=self.name,
                error=str(e),
                exc_info=True,
            )
            raise WorkflowExecutionError(
                f"Unexpected graph error: {str(e)}",
                partial_state=state.model_dump(),
                original_exception=e,
                action_name=self.name,
            ) from e
