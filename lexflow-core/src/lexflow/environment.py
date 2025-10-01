from typing import Any, Optional


class Scope:
    """Simple scope management."""

    def __init__(self, parent: Optional["Scope"] = None):
        self.vars = {}
        self.parent = parent

    def __setitem__(self, name: str, value: Any):
        """Set variable in current scope."""
        self.vars[name] = value

    def __getitem__(self, name: str) -> Any:
        """Get variable, searching up scope chain."""
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent[name]
        raise KeyError(f"Undefined variable: {name}")

    def __contains__(self, name: str) -> bool:
        """Check if variable exists."""
        return name in self.vars or (self.parent and name in self.parent)

    def set(self, name: str, value: Any):
        """Update existing variable (searches up chain)."""
        if name in self.vars:
            self.vars[name] = value

        elif self.parent and name in self.parent:
            self.parent.set(name, value)
        else:
            raise KeyError(f"Cannot assign to undefined variable: {name}")

    def __repr__(self):
        return f"Scope({list(self.vars.keys())})"
