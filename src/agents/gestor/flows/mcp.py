import logging
import json

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from langgraph.types import interrupt

from core.llm import get_configured_model
from core import settings

from agents.gestor.core.states import GestorState
from agents.gestor.core.utils import wrap_model, get_last_user_message


logger = logging.getLogger(__name__)

async def welcome_node(state: GestorState, config: RunnableConfig) -> GestorState:
    """
    Node to welcome the user and initialize the state.
    """
    logger.info("[welcome_node] Iniciando o fluxo de boas-vindas.")
    response = ...
    return {"messages": [AIMessage(content="response")]}

async def identify_intents(state: GestorState, config: RunnableConfig, store: BaseStore) -> GestorState:
    """
    Node to identify the user's intent based on the messages.
    """
    logger.info("[identify_intent] Identificando a intenção do usuário.")
    
    # Setup store configuration
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    namespace = (user_id,) if user_id else None
    key = "intent"

    if namespace:
        try:
            stored_intent = await store.get(namespace, key)
            if stored_intent:
                logger.info(f"[identify_intent] Intent recuperada do armazenamento: {stored_intent}")
                state["user_intent"] = stored_intent
                return state