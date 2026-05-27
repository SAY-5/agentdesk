"""Tool interface that the agent calls into the backend."""

from agentdesk.tools.registry import (
    TOOLS,
    ToolError,
    ToolRegistry,
    ToolSpec,
    build_registry,
)

__all__ = ["TOOLS", "ToolError", "ToolRegistry", "ToolSpec", "build_registry"]
