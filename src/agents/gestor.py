from typing import List, Dict, Optional, TypedDict, Any
from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import AIMessage, HumanMessage
import requests
import json

# Configurações
MANDU_API_URL = "https://api.sobdemanda.mandu.piaui.pro/v1/chat/completions"
MANDU_API_KEY = "sk-7tYgDXM2_Oekl0NHGYyTBA"
GESTOR_API_URL = "https://mcp.gestor.sead.pi.gov.br"


# Modelo de Estado
class AppState(MessagesState):
    api_intent: Optional[Dict[str, Any]]
    api_response: Optional[Dict[str, Any]]
    error: Optional[str]

# Função para chamar o LLM e identificar a intenção
def identify_intent(state: AppState) -> AppState:
    system_prompt = """Você é um assistente classificador de intenções para o sistema SEAD.
    Responda sempre em português do Brasil, nunca em inglês.
    Identifique a intenção e extraia parâmetros relevantes, retornando APENAS JSON:

    Opções:
    1. {"intent": "pessoa", "parameters": {"nome": "Nome Completo"}}
    2. {"intent": "objetivo", "parameters": {"orgao": "Nome", "setor": "Setor"}} 
    3. {"intent": "hierarquia", "parameters": {"orgao": "Nome"}}
    4. {"intent": "outro", "response": "Resposta direta"}

    Exemplo 1: "Quem é João Silva?" → {"intent": "pessoa", "parameters": {"nome": "João Silva"}}
    Exemplo 2: "Objetivos da SEAD" → {"intent": "objetivo", "parameters": {"orgao": "SEAD"}}
    """
    
    try:
        response = requests.post(
            MANDU_API_URL,
            json={
                "model": "Qwen/Qwen3-30B-A3B",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": state["messages"][-1].content}
                ],
                "temperature": 0.1
            },
            headers={
                "Authorization": f"Bearer {MANDU_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        state["api_intent"] = json.loads(content)
        
    except Exception as e:
        state["error"] = f"Erro ao identificar intenção: {str(e)}"
    
    return state

# Função para chamar a API adequada
def call_api(state: AppState) -> AppState:
    if not state.get("api_intent"):
        return state
    
    intent = state["api_intent"].get("intent")
    params = state["api_intent"].get("parameters", {})
    
    try:
        if intent == "pessoa":
            response = requests.post(
                f"{GESTOR_API_URL}/pessoa/",
                json={"nome": params.get("nome")},
                headers={"Content-Type": "application/json"},
                verify=False
            )
            state["api_response"] = response.json()
            
        elif intent == "objetivo":
            response = requests.post(
                f"{GESTOR_API_URL}/objetivo-estrategico/",
                json={
                    "orgao": params.get("orgao"),
                    "setor": params.get("setor")
                },
                headers={"Content-Type": "application/json"},
                verify=False
            )
            state["api_response"] = response.json()
            
        elif intent == "hierarquia":
            response = requests.post(
                f"{GESTOR_API_URL}/hierarquia-entidades/",
                json={"orgao": params.get("orgao")},
                headers={"Content-Type": "application/json"},
                verify=False
            )
            state["api_response"] = response.json()
            
    except Exception as e:
        state["error"] = f"Erro na API: {str(e)}"
    
    return state

# criar função de parse da string para mensagem

def parse_string_to_message(text: str):
    """
    Converte uma string em uma mensagem do tipo AIMessage.
    """
    return AIMessage(content=text)
    

# Função para gerar resposta natural
def generate_response(state: AppState) -> AppState:
    print("Entrou em generate_response")
    if state.get("error"):
        print(f"Erro detectado no estado: {state['error']}")
        state["message"] = "Desculpe, ocorreu um erro. Por favor, tente novamente."
        mensagem = parse_string_to_message(state["message"])
        state["messages"].append(mensagem)
        print("Mensagem de erro adicionada ao estado.")
        return state

    intent = state["api_intent"].get("intent")
    print(f"Intenção identificada: {intent}")

    if intent == "outro":
        print("Intenção 'outro' detectada. Fazendo chamada direta para a IA.")
        # Busca a última mensagem do usuário (HumanMessage)
        ultima_mensagem_usuario = None
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                ultima_mensagem_usuario = msg.content
                break

        if ultima_mensagem_usuario is None:
            ultima_mensagem_usuario = ""

        try:
            response = requests.post(
                MANDU_API_URL,
                json={
                    "model": "Qwen/Qwen3-30B-A3B",
                    "messages": [
                        {"role": "user", "content": ultima_mensagem_usuario}
                    ],
                    "temperature": 0.3
                },
                headers={
                    "Authorization": f"Bearer {MANDU_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            state["message"] = response.json()["choices"][0]["message"]["content"]
            print("Resposta natural recebida da IA para intenção 'outro'.")
        except Exception as e:
            print(f"Erro ao chamar a IA para intenção 'outro': {e}")
            state["message"] = "Não consegui obter uma resposta natural."
        mensagem = parse_string_to_message(state["message"])
        state["messages"].append(mensagem)
        print("Mensagem para intenção 'outro' adicionada ao estado.")
        return state

    system_prompt = f"""Você é um assistente que transforma dados JSON em respostas naturais.
    Dados recebidos: {json.dumps(state.get("api_response"))}
    
    Regras:
    - Seja claro e conciso
    - Para listas vazias, explique educadamente
    - Destaque informações principais
    - Responda sempre em português, você está localizada no Brasil
    """
    # Busca a última mensagem do usuário (HumanMessage)
    ultima_mensagem_usuario = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            ultima_mensagem_usuario = msg.content
            break

    if ultima_mensagem_usuario is None:
        ultima_mensagem_usuario = ""

    user_prompt = f'Transforme estes dados em uma resposta para: "{ultima_mensagem_usuario}"'

    try:
        print("Enviando requisição para o MANDU_API_URL...")
        response = requests.post(
            MANDU_API_URL,
            json={
                "model": "Qwen/Qwen3-30B-A3B",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3
            },
            headers={
                "Authorization": f"Bearer {MANDU_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        print("Resposta recebida da API com sucesso.")
        state["message"] = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Erro ao chamar a API do Mandu: {e}")
        state["message"] = "Não consegui formatar a resposta."

    mensagem = parse_string_to_message(state["message"])
    state["messages"].append(mensagem)
    print("Mensagem final adicionada ao estado.")
    return state

# Configuração do Grafo
graph = StateGraph(AppState)

graph.add_node("identify_intent", identify_intent)
graph.add_node("call_api", call_api)
graph.add_node("generate_response", generate_response)

graph.set_entry_point("identify_intent")
graph.add_edge("identify_intent", "call_api")
graph.add_edge("call_api", "generate_response")
graph.add_edge("generate_response", END)

app = graph.compile()