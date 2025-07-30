from typing import Any, cast

from langchain_core.language_models.base import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableLambda, RunnableSerializable

from .states import BOState


def _prepare_messages(state: BOState, system_prompt: BaseMessage) -> list[BaseMessage]:
    """Helper function to prepare messages for the model."""
    return [system_prompt] + state.get("messages", [])


def wrap_model(
    model: BaseChatModel | Runnable[LanguageModelInput, Any], system_prompt: BaseMessage
) -> RunnableSerializable[BOState, Any]:
    """Wrapper for the model with state preprocessing."""
    preprocessor = RunnableLambda(
        lambda state: _prepare_messages(cast(BOState, state), system_prompt),
        name="StateModifier",
    )
    return preprocessor | model


def get_last_user_message(state: BOState) -> str:
    """Extract the last user message from state."""
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                return str(msg.content)
    return ""
