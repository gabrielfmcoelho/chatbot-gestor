from typing import Literal, List, Dict, Any, Optional, cast
from agents.gestor.core.models import IntentClassification

from langgraph.graph import MessagesState

class GestorState(MessagesState, total=False):
    first_run: bool = True
    conversation_context: str | None
    last_user_message: str | None
    intents: IntentClassification | None
    tools_responses: Optional[Dict[str, Any]] | None
    tool_calls_pending: bool = False
    # Cache for MCP tool metadata to avoid refetching (serializable)
    cached_tools_metadata: Optional[List[Dict[str, Any]]] | None
    cached_tools_timestamp: Optional[float] | None
    # Track tool execution to prevent duplicates
    executed_tool_calls: Optional[List[str]] | None
    # Response size management
    large_responses_summary: Optional[Dict[str, str]] | None