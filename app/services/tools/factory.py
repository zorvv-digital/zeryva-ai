import re
import logging
from typing import Callable, Sequence, Any
from app.db.models import ToolModel

logger = logging.getLogger(__name__)


class ToolFactory:
    """
    Factory pattern for dynamically instantiating Agno-compatible tools from database ToolModel records.

    Polymorphic Dispatch:
    - 'text_context': Generates a dynamic Python function returning raw document/FAQ text context.
    - Future Tool Types ('agentic_rag', 'sql_query', 'web_search', 'google_sheets', 'http_request'):
      Can be registered here without modifying the database schema.
    """

    @classmethod
    def create_tool(cls, tool_model: ToolModel) -> Callable:
        """
        Converts a single database ToolModel into a callable Agno runtime tool.

        Args:
            tool_model (ToolModel): Database record containing tool definition and JSON config.

        Returns:
            Callable: Agno-compatible python tool function.
        """
        tool_type = tool_model.tool_type.lower() if tool_model.tool_type else "text_context"

        if tool_type == "text_context":
            return cls._create_text_context_tool(
                name=tool_model.name,
                description=tool_model.description,
                config=tool_model.config or {},
            )
        else:
            # Fallback for future tool types prior to full provider implementation
            logger.warning(
                f"Tool type '{tool_type}' encountered for tool '{tool_model.name}'. Falling back to default text context generator."
            )
            return cls._create_text_context_tool(
                name=tool_model.name,
                description=tool_model.description,
                config=tool_model.config or {},
            )

    @classmethod
    def create_tools(cls, tool_models: Sequence[ToolModel]) -> list[Callable]:
        """
        Converts a sequence of database ToolModel records into a list of callable Agno tools.

        Args:
            tool_models (Sequence[ToolModel]): Sequence of active tool DB records.

        Returns:
            list[Callable]: List of callable Agno tool functions ready for Agent(tools=[...]).
        """
        return [cls.create_tool(tool) for tool in tool_models]

    @staticmethod
    def _create_text_context_tool(name: str, description: str, config: dict[str, Any]) -> Callable:
        """
        Constructs a dynamic callable function for text_context tools (FAQs, terms, policies).
        """
        raw_content = config.get("content", "")

        def text_context_fn() -> str:
            return raw_content

        # Sanitize function name for Python identifier compliance (alphanumeric & underscores)
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", name).lower().strip("_")
        if not clean_name:
            clean_name = "custom_text_tool"

        text_context_fn.__name__ = clean_name
        text_context_fn.__doc__ = description.strip()
        return text_context_fn
