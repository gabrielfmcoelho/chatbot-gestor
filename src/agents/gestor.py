from typing import List, Dict, Optional, TypedDict, Any
from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações
MANDU_API_URL = "https://api.sobdemanda.mandu.piaui.pro/v1/chat/completions"
MANDU_API_KEY = "sk-7tYgDXM2_Oekl0NHGYyTBA"
GESTOR_API_URL = "https://mcp.gestor.sead.pi.gov.br"
MCP_TOOLS_INFO = "/mcp"

# Modelo de Estado
class AppState(MessagesState):
    api_intent: Optional[Dict[str, Any]]
    api_response: Optional[Dict[str, Any]]
    error: Optional[str]


def original_discover_mcp_tools() -> List[Dict[str, Any]]:
    tool_info_url = f"{GESTOR_API_URL}{MCP_TOOLS_INFO}"
    print(f"Descobrindo ferramentas MCP de: {tool_info_url}")
    response = requests.get(tool_info_url, verify=False)
    response.raise_for_status()
    return response.json()
    
# Função para chamar o LLM e identificar a intenção
def identify_intent(state: AppState) -> AppState:
    system_prompt = """Você é um assistente especializado em classificação de intenções para o sistema SEAD, com capacidade de integrar dados via API. 
    Siga estritamente estas diretrizes:\n\n1. LINGUAGEM:\n- Responda APENAS em português do Brasil\n- Use linguagem formal e técnica adequada para servidores públicos\n\n2. 
    PROCESSAMENTO:\n- Analise a intenção com precisão antes de responder\n- Extraia parâmetros de forma minuciosa\n- Mantenha respostas curtas e objetivas (máximo 2 frases quando diretas)\n\n3. 
    FORMATO DE SAÍDA:\n- Para classificações: APENAS JSON estruturado\n- 
    Para respostas diretas: texto claro e conciso\n\n4. OPÇÕES DE INTENÇÃO:\n{\n  \"pessoa\": {\n    \"descrição\": \"Consultar dados de servidor\",\n    
    \"parâmetros\": {\"nome\": \"Nome Completo (exato)\"},\n    \"exemplo\": \"Quem é Maria Souza? → {\"intent\": \"pessoa\", \"parameters\": {\"nome\": \"Maria Souza\"}}\"\n  },\n  \"objetivo\": {\n    \"descrição\": \"Consultar objetivos institucionais\",\n    \"parâmetros\": {\"orgao\": \"Nome Oficial\", \"setor\": \"Opcional\"},\n    \"exemplo\": \"Quais os objetivos da PRODAM? → {\"intent\": \"objetivo\", \"parameters\": {\"orgao\": \"PRODAM\"}}\"\n  },\n  \"hierarquia\": {\n    \"descrição\": \"Estrutura organizacional\",\n    \"parâmetros\": {\"orgao\": \"Nome Oficial\"},\n    \"exemplo\": \"Mostre a estrutura da SEGOV → {\"intent\": \"hierarquia\", \"parameters\": {\"orgao\": \"SEGOV\"}}\"\n  },\n  \"outro\": {\n    \"descrição\": \"Demais assuntos\",\n    
    \"response\": \"Resposta direta e objetiva\"\n  }\n}\n\n5. VALIDAÇÃO:\n- Confirme siglas antes de consultar (ex: \"SEAD\" ≠ \"SED\") \n- Para nomes incompletos, solicite complemento: \"Poderia confirmar o nome completo?\"\n- Em ambiguidades, enumere opções claras\n\n6. PERFORMANCE:\n- Priorize velocidade de resposta\n- Mantenha consistência terminológica\n- Documente eventuais limitações de dados
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
    print(f"Chamando API para a intenção: {intent}")
    params = state["api_intent"].get("parameters", {})
    print(f"Parâmetros recebidos: {params}")
    
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

        print(f"Resposta da API: {state['api_response']}")
            
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