from typing import Optional, Dict, Any, List
from pathlib import Path


class LexFlowError(Exception):
    """Base exception for all Lex Flow errors"""


class JSONParseError(LexFlowError):
    def __init__(
        self,
        message: str,
        file_path: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ):
        self.file_path = file_path
        self.line = line
        self.column = column
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        location = f"in {Path(self.file_path).name}"
        if self.line:
            location += f" at line {self.line}"
            if self.column:
                location += f", column {self.column}"
        return f"JSON Error {location}: {message}"


class WorkflowValidationError(LexFlowError):
    """Workflow structure and dependency validation errors"""

    def __init__(
        self, message: str, workflow_name: str, file_path: Optional[str] = None
    ):
        self.workflow_name = workflow_name
        self.file_path = file_path
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        location = f"in workflow '{self.workflow_name}'"
        if self.file_path:
            location += f" ({Path(self.file_path).name})"
        return f"Validation Error {location}: {message}"


class RuntimeError(LexFlowError):
    def __init__(
        self,
        message: str,
        workflow_name: str,
        node_id: Optional[str] = None,
        opcode: Optional[str] = None,
        call_stack: Optional[List[str]] = None,
        variables: Optional[Dict[str, Any]] = None,
    ):
        self.workflow_name = workflow_name
        self.node_id = node_id
        self.opcode = opcode
        self.call_stack = call_stack or []
        self.variables = variables or {}
        super().__init__(self._format_message(message))

    def _format_message(self, message: str) -> str:
        context = f"Runtime Error in workflow '{self.workflow_name}'"
        if self.node_id:
            context += f", node '{self.node_id}'"
        if self.opcode:
            context += f" (opcode: {self.opcode})"

        details = f"{context}: {message}"

        if self.call_stack:
            details += "\n\nCall Stack:\n"
            for i, frame in enumerate(reversed(self.call_stack)):
                details += f"  {i + 1}. {frame}\n"

        return details


class WorkflowNotFoundError(LexFlowError):
    """Workflow dependency not found"""

    def __init__(self, workflow_name: str, referenced_from: Optional[str] = None):
        self.workflow_name = workflow_name
        self.referenced_from = referenced_from
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        message = f"Workflow '{self.workflow_name}' not found"
        if self.referenced_from:
            message += f" (referenced from workflow '{self.referenced_from}')"
        return message


class ErrorReporter:
    """Centralized error reporting with helpful suggestions"""

    @staticmethod
    def suggest_fixes(error: Exception) -> List[str]:
        suggestions = []

        if isinstance(error, JSONParseError):
            suggestions.extend(
                [
                    "Check for missing commas, quotes, or brackets",
                    "Validate JSON syntax using a JSON linter",
                    "Ensure all strings are properly quoted",
                ]
            )

        elif isinstance(error, WorkflowValidationError):
            if "workflow_start" in str(error):
                suggestions.append("Add a 'workflow_start' node as the entry point")
            if "interface" in str(error):
                suggestions.append("Add an 'interface' field with inputs/outputs")

        elif isinstance(error, WorkflowNotFoundError):
            suggestions.extend(
                [
                    f"Check if '{error.workflow_name}' is defined in any input files",
                    "Verify workflow names are spelled correctly",
                    "Ensure all required files are included",
                ]
            )

        return suggestions

    @staticmethod
    def format_error_report(
        error: Exception, suggestions: Optional[List[str]] = None
    ) -> str:
        report = f"[ERROR] {error}\n"

        if not suggestions:
            suggestions = ErrorReporter.suggest_fixes(error)

        if suggestions:
            report += "\nSuggestions:\n"
            for i, suggestion in enumerate(suggestions, 1):
                report += f"  {i}. {suggestion}\n"

        return report
