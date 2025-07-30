from typing import Literal, List

from langgraph.graph import MessagesState

class GestorState(MessagesState, total=False):
    user_intents: Optional[Dict[str, Any]]
    tools_to_use: Optional[Dict[str, Any]]
    tool_responses: Optional[Dict(str, Any)]
    tool_errors: Optional[List(str)]