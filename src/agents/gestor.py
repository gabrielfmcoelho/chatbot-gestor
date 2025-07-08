from typing import Dict, Optional, Any
from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import AIMessage, SystemMessage
from core import get_model, settings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import (
    RunnableConfig,
    RunnableLambda,
    RunnableSerializable,
)
import requests
import json

# Configurações
GESTOR_API_URL = "https://mcp.gestor.sead.pi.gov.br"
# 

# Modelo de Estado
class AgentState(MessagesState, total=False):
    api_intent: Optional[Dict[str, Any]]
    api_response: Optional[Dict[str, Any]]
    error: Optional[str]

def wrap_model(model: BaseChatModel, instructions: str) -> RunnableSerializable[AgentState, AIMessage]:
    def add_system_and_user(state):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) and m.content == instructions for m in messages):
            messages = [SystemMessage(content=instructions)] + messages
        return messages
    preprocessor = RunnableLambda(add_system_and_user, name="StateModifier")
    return preprocessor | model  # O modelo deve vir DEPOIS do preprocessor

async def acall_model(state: AgentState, config: RunnableConfig, instructions: str) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m, instructions)
    messages = state["messages"]
    response = await model_runnable.ainvoke(messages, config)
    print("DEBUG acall_model response:", response)
    return {"messages": [response]}

def ensure_dict(obj):
    # Desce recursivamente até encontrar um dicionário
    while isinstance(obj, list) and len(obj) > 0:
        obj = obj[0]
    if not isinstance(obj, dict):
        raise ValueError("Resposta do modelo não é um dicionário JSON válido.")
    return obj

async def identify_intent(state: AgentState, config: RunnableConfig) -> AgentState:
    system_prompt = """Você é um classificador de intenções para o sistema SEAD. 
    Identifique a intenção e extraia parâmetros relevantes, retornando APENAS JSON:

    Opções:
    1. {\"intent\": \"pessoa\", \"parameters\": {\"nome\": \"Nome Completo\"}}
    2. {\"intent\": \"objetivo\", \"parameters\": {\"orgao\": \"Nome\", \"setor\": \"Setor\"}} 
    3. {\"intent\": \"hierarquia\", \"parameters\": {\"orgao\": \"Nome\"}}
    4. {\"intent\": \"outro\", \"response\": \"Resposta direta\"}

    Exemplo 1: \"Quem é João Silva?\" → {\"intent\": \"pessoa\", \"parameters\": {\"nome\": \"João Silva\"}}
    Exemplo 2: \"Objetivos da SEAD\" → {\"intent\": \"objetivo\", \"parameters\": {\"orgao\": \"SEAD\"}}
    Exemplo 3: \"Oi\" → {\"intent\": \"outro\"}
    """
    try:
        print(f"1. system_prompt: {state['messages']}")
        new_state = await acall_model(state, config, system_prompt)
        messages = new_state.get("messages")
        print("DEBUG messages:", messages)
        last_message = messages[-1]
        content = getattr(last_message, "content", None)
        print("DEBUG content:", content)
        if not content:
            raise ValueError("Mensagem retornada sem conteúdo válido.")
        # Usa a função utilitária para garantir dicionário
        state["api_intent"] = ensure_dict(json.loads(content))
        print("DEBUG api_intent (dict):", state["api_intent"])
    except Exception as e:
        state["error"] = f"Erro ao identificar intenção: {str(e)}"
        print(f"Erro ao identificar intenção: {str(e)}")

    return state


def call_api(state: AgentState) -> AgentState:
    if not state.get("api_intent"):
        print("intenção não identificada")
        return state

    print("DEBUG call_api api_intent:", state["api_intent"])
    if not isinstance(state["api_intent"], dict):
        state["error"] = "api_intent não é um dicionário em call_api"
        print("Erro: api_intent não é um dicionário em call_api")
        return state

    intent = state["api_intent"].get("intent")
    params = state["api_intent"].get("parameters", {})

    try:
        if intent == "pessoa":
            response = requests.get(f"{GESTOR_API_URL}/pessoa", params=params)
        elif intent == "objetivo":
            response = requests.get(f"{GESTOR_API_URL}/objetivo-estrategico", params=params)
        elif intent == "hierarquia":
            response = requests.get(f"{GESTOR_API_URL}/hierarquia-entidades", params=params)
        else:
            state["api_response"] = {"error": "Intenção não suportada"}
            return state

        state["api_response"] = response.json()
    except Exception as e:
        state["error"] = f"Erro na consulta à API: {str(e)}"
        print("erro api")

    return state

def format_mock_message(message_string: str) -> AIMessage:
    content = (message_string)
    return AIMessage(content=content)

def format_response(response: dict) -> AIMessage:
    message = AIMessage(
        content=response.get("choices")[0].get("message").get("content")
    )
    return message

# Função para gerar resposta natural usando o modelo local
async def generate_response(state: AgentState, config: RunnableConfig) -> AgentState:
    if state.get("error"):
        state["messages"] = [format_mock_message("Desculpe, ocorreu um erro. Por favor, tente novamente.")]
        return state

    intent = state.get("api_intent", {}).get("intent")
    if not intent:
        state["messages"] = [format_mock_message("Não consegui identificar sua intenção.")]
        return state

    if intent == "outro":
        state["messages"] = [format_mock_message("Não entendi sua pergunta.")]
        return state

    api_response = state.get("api_response")
    if not api_response:
        state["messages"] = [format_mock_message("Não obtive resposta da base de dados.")]
        return state

    system_prompt = (
        "Você é um assistente que transforma dados JSON em respostas naturais.\n"
        f"Dados recebidos: {json.dumps(api_response, ensure_ascii=False)}\n\n"
        "Regras:\n"
        "- Seja claro e conciso\n"
        "- Para listas vazias, explique educadamente\n"
        "- Destaque informações principais\n"
    )
    user_prompt = f'Transforme estes dados em uma resposta para: "{state["messages"][-1].content}"'

    state["messages"] = [
        SystemMessage(content=system_prompt),
        AIMessage(content=user_prompt)
    ]

    try:
        new_state = await acall_model(state, config, system_prompt)
        state["messages"] = new_state.get("messages")
    except Exception as e:
        state["messages"] = [format_mock_message("Não consegui formatar a resposta. Erro técnico.")]
        print(f"Erro ao gerar resposta natural: {e}")

    return state

# Configuração do Grafo
graph = StateGraph(AgentState)

graph.add_node("identify_intent", identify_intent)
graph.add_node("call_api", call_api)
graph.add_node("generate_response", generate_response)

graph.set_entry_point("identify_intent")
graph.add_edge("identify_intent", "call_api")
graph.add_edge("call_api", "generate_response")
graph.add_edge("generate_response", END)

app = graph.compile()