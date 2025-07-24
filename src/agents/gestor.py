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

orgaos_validos = [
  {
    "SEAD - Secretaria de Administração": {
      "Cnpj": "06.553.481/0003-00",
      "Endereco": "Av. Pedro Freitas, 1900, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "SAF - Secretaria da Agricultura Familiar": {
      "Cnpj": "06.553.572/0001-84",
      "Endereco": "Rua João Cabral, nº 2319",
      "Telefone": ""
    }
  },
  {
    "SECULT - Secretaria da Cultura": {
      "Cnpj": "05.782.352/0001-60",
      "Endereco": "Praça Marechal Deodoro, 816",
      "Telefone": ""
    }
  },
  {
    "SEDUC - Secretaria da Educação": {
      "Cnpj": "06.554.729/0001-96",
      "Endereco": "Av. Pedro Freitas, S/N\n, Centro Administrativo,  Bloco D/F",
      "Telefone": ""
    }
  },
  {
    "SEFAZ - Secretaria da Fazenda": {
      "Cnpj": "06.553.556/0001-91",
      "Endereco": "Av. Pedro Freitas, 1900, Centro Administrativo, Bloco C, 2º Andar",
      "Telefone": ""
    }
  },
  {
    "SEINFRA - Secretaria da Infraestrutura": {
      "Cnpj": "06.553.531/0001-98",
      "Endereco": "Av. Pedro Freitas, S/Nº, Bloco G, 1º andar - Centro Administrativo",
      "Telefone": ""
    }
  },
  {
    "SEJUS - Secretaria da Justiça": {
      "Cnpj": "07.217.342/0001-07",
      "Endereco": "Av. Pedro Freitas - Bloco G 2º Andar - Centro Administrativo\n Teresina-PI - 64018-200",
      "Telefone": "(86) 99488 8133"
    }
  },
  {
    "SESAPI - Secretaria da Saúde": {
      "Cnpj": "06.553.564/0001-38",
      "Endereco": "Avenida Pedro Freitas, Teresina, PI, 64018-000 ",
      "Telefone": "(86) 3216-3610"
    }
  },
  {
    "SSP - Secretaria da Segurança Pública": {
      "Cnpj": "06.553.549/0001-90",
      "Endereco": "R. Walfran Batista, 91 - São Cristóvão - CEP.: 64.046-470 - Teresina - PI",
      "Telefone": "(86) 3216 5221 "
    }
  },
  {
    "SECID - Secretaria das Cidades": {
      "Cnpj": "08.767.094/0001-30",
      "Endereco": "Rua Acésio do Rêgo Monteiro, Nº 1515, Edificio Antonio Portela Barbosa",
      "Telefone": ""
    }
  },
  {
    "SEMPI - Secretaria das Mulheres": {
      "Cnpj": "19.970.278/0001-10",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "SEAGRO - Secretaria do Agronegócio e Empreendedorismo Rural": {
      "Cnpj": "33.691.623/0001-07",
      "Endereco": "Rua David Caldas, 134, 3° andar, Centro - Sul, 64000-916",
      "Telefone": ""
    }
  },
  {
    "SADA - Secretaria da Assistência Técnica e Defesa Agropecuária": {
      "Cnpj": "06.688.451/0001-40",
      "Endereco": "Rua João Cabral, 2319. Teresina-PI",
      "Telefone": ""
    }
  },
  {
    "SASC - Secretaria da Assistência Social, Trabalho e Direitos Humanos": {
      "Cnpj": "09.579.079/0001-21",
      "Endereco": "Rua Acre, 340, Cabral\t, 64014-042",
      "Telefone": ""
    }
  },
  {
    "SEDEC - Secretaria da Defesa Civil": {
      "Cnpj": "08.789.777/0001-99",
      "Endereco": "Rua Jaicós,\n1435 - Ilhotas 64014-060",
      "Telefone": ""
    }
  },
  {
    "SDE - Secretaria do Desenvolvimento Econômico": {
      "Cnpj": "06.688.303/0001-25",
      "Endereco": "Av. Industrial Gil Martins, 1810\tEd. Albano Franco - 3° e 4° andares, Redenção\n",
      "Telefone": ""
    }
  },
  {
    "SEDRAMER - Secretaria do Desenvolvimento, Abastecimento, Mineração e Energias Renováveis": {
      "Cnpj": "14.862.788/0001-50",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "SEID - Secretaria da Inclusão da Pessoa com Deficiência": {
      "Cnpj": "05.735.244/0001-36",
      "Endereco": "Rua Álvaro Mendes, Nº 1432, Próx. aos Correios - Esq. com 7 de Setembro, Centro - Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "SEFIR - Secretaria da Irrigação e Infraestrutura Hídrica": {
      "Cnpj": "22.911.207/0001-50",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "SEMARH - Secretaria do Meio Ambiente e Recursos Hídricos": {
      "Cnpj": "12.176.046/0001-45",
      "Endereco": "Rua Odilon Araújo, 1035, Piçarra\n, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "SEPLAN - Secretaria do Planejamento": {
      "Cnpj": "06.553.523/0001-41",
      "Endereco": "Avenida Miguel Rosa, 3190, Centro/Sul, Térreo, Centro",
      "Telefone": ""
    }
  },
  {
    "SETUR - Secretaria do Turismo": {
      "Cnpj": "08.783.132/0001-49",
      "Endereco": "Av. Antonino Freire, 1473, 2° Andar, Centro, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "SECEPI - Secretaria dos Esportes": {
      "Cnpj": "49.497.879/0001-18",
      "Endereco": "Av. Pedro Freitas, s/nº, Bloco G, 2° andar • Centro Administrativo , CEP: 64.018-900 Teresina-PI",
      "Telefone": ""
    }
  },
  {
    "SETRANS - Secretaria dos Transportes": {
      "Cnpj": "08.809.355/0001-38",
      "Endereco": "Av. Pedro Freitas, s/nº, Bloco G, 1º andar, Centro Administrativo, São Pedro",
      "Telefone": ""
    }
  },
  {
    "CCOM - Coordenadoria de Comunicação": {
      "Cnpj": "05.810.478/0001-09",
      "Endereco": "Av. Antonino Freire, 1396, Centro - Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "COJUV - Coordenadoria da Juventude": {
      "Cnpj": "13.089.639/0001-37",
      "Endereco": "Avenida Antonino Freire, 1473, Edifício D. Antonirta Araújo, 4°Andar, Centro",
      "Telefone": ""
    }
  },
  {
    "CENDFOL - Coordenadoria de Enfrentamento às Drogas e Fomento ao Lazer": {
      "Cnpj": "15.029.783/0001-03",
      "Endereco": "Av. Antonino Freire, 1473, 1º Andar, Centro\n",
      "Telefone": ""
    }
  },
  {
    "CDTER - Coordenadoria de Desenvolvimento dos Territórios": {
      "Cnpj": "27.431.506/0001-01",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "PGE - Procuradoria Geral do Estado": {
      "Cnpj": "06.553.481/0004-91",
      "Endereco": "Av. Senador Arêa Leão nº 1650, Térreo, Jockey Club",
      "Telefone": ""
    }
  },
  {
    "ADAPI - Agência de Defesa Agropecuária do Estado do Piauí": {
      "Cnpj": "07.812.549/0001-20",
      "Endereco": "Rua 19 de Novembro, 1980, Morro da Esperança",
      "Telefone": ""
    }
  },
  {
    "ADH - Agência de Desenvolvimento Habitacional do Piauí": {
      "Cnpj": "08.787.769/0001-03",
      "Endereco": "Av. José dos Santos e Silva, nº 1155, Centro, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "AGRESPI - Agência Reguladora dos Serviços Públicos Delegados do Estado do Piauí": {
      "Cnpj": "30.128.386/0001-82",
      "Endereco": "Av. João XXIII, 5325, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "CGE - Controladoria Geral do Estado": {
      "Cnpj": "05.776.789/0001-90",
      "Endereco": "Av. Pedro Freitas, 1900, Centro Administrativo, Bloco C, 2º Andar, São Pedro\n",
      "Telefone": ""
    }
  },
  {
    "CBMEPI - Corpo de Bombeiros Militar do Estado do Piauí": {
      "Cnpj": "05.485.613/0001-80",
      "Endereco": "Av. Miguel Rosa, 3515, Terreo, Piçarra, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "DER - Departamento de Estradas de Rodagem do Piauí": {
      "Cnpj": "06.535.751/0001-99",
      "Endereco": "Avenida Frei Serafim, 2492, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "DETRAN - Departamento Estadual de Trânsito": {
      "Cnpj": "06.535.926/0001-68",
      "Endereco": "Avenida Gil Martins, 2000, Redenção, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "FAPEPI - Fundação de Amparo a Pesquisa do Estado do Piauí": {
      "Cnpj": "00.422.744/0001-02",
      "Endereco": "Av. Odilon Araújo, 372, 1º Andar, Piçarra",
      "Telefone": ""
    }
  },
  {
    "PIAUIPREV - Fundação Piauí Previdência": {
      "Cnpj": "26.895.877/0001-81",
      "Endereco": "Av. Pedro Freitas, 1904, Centro Administrativo, Edifício Jornalista Carlos Castelo Branco, São Pedro\n",
      "Telefone": ""
    }
  },
  {
    "TVANTARES - Fundação Rádio e Televisão Educativa do Piauí": {
      "Cnpj": "05.787.268/0001-39",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "UESPI - Fundação Universidade Estadual do Piauí": {
      "Cnpj": "07.471.758/0001-57",
      "Endereco": "Rua João Cabral,  2231, Pirajá, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "GAMIL - Gabinete Militar": {
      "Cnpj": "06.553.481/0002-20",
      "Endereco": "Av. Antonino Freire, 1450, Palácio de Karnak, Centro",
      "Telefone": ""
    }
  },
  {
    "IAEPI - Instituto de Águas e Esgotos do Piauí": {
      "Cnpj": "22.057.819/0001-28",
      "Endereco": "Av. Presidente Kennedy, 570, São Cristóvão, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "IASPI - Instituto de Assistência à Saúde dos Servidores Públicos do Estado do Piauí": {
      "Cnpj": "06.857.213/0001-10",
      "Endereco": "Rua Sete de Setembro, 121, Centro, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "EMATER - Instituto de Assistência Técnica e Extensão Rural do Piauí": {
      "Cnpj": "06.688.451/0001-40",
      "Endereco": "Rua João Cabral, 2319. Teresina-PI",
      "Telefone": ""
    }
  },
  {
    "IDEPI - Instituto de Desenvolvimento do Piauí": {
      "Cnpj": "09.034.960/0001-47",
      "Endereco": "Rua Altos, 277, Térreo, Primavera, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "IMEPI - Instituto de Metrologia do Estado do Piauí": {
      "Cnpj": "41.522.079/0001-06",
      "Endereco": "Av. Barão de Gurguéia, nº 3336, Tabuleta\n, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "INTERPI - Instituto de Terras do Piauí": {
      "Cnpj": "06.718.282/0001-43",
      "Endereco": "Rua Coelho Rodrigues 1647, Teresina, PI, 64000-080",
      "Telefone": "(86) 3221-2449"
    }
  },
  {
    "JUCEPI - Junta Comercial do Estado do Piauí": {
      "Cnpj": "06.690.994/0001-00",
      "Endereco": "Rua Gen. Osório, 3002, Palácio Vitória, Cabral\n, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "PMPI - Polícia Militar do Estado do Piauí": {
      "Cnpj": "07.444.159/0001-44",
      "Endereco": "AV Higino Cunha, 1750, Quartel do Comando Geral, Cristo Rei",
      "Telefone": ""
    }
  },
  {
    "VICEGOV - Vice-Governadoria": {
      "Cnpj": "",
      "Endereco": "R. Paissandu, 1456, Centro (Sul), Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "SEGOV - Secretaria de Governo": {
      "Cnpj": "06.553.499/0001-40",
      "Endereco": "Av. Antonino Freire, 1450, Palácio de Karnak, Centro",
      "Telefone": ""
    }
  },
  {
    "CONSED - Conselho Estadual de Educação": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "INVESTEPIAUI - Agência de Atração de Investimentos Estratégicos do Piauí": {
      "Cnpj": "",
      "Endereco": "Av Pedro Freitas, s/n, Bloco C, 1° Andar, Centro Administrativo, São Pedro",
      "Telefone": ""
    }
  },
  {
    "SERES - Secretaria de Relações Sociais": {
      "Cnpj": "",
      "Endereco": "Av. Antonino Freire, 1473, Centro, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "GABGOV - Gabinete do Governador": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "DPE - Defensoria Publica": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "SURPI - Superintendência de Representação do Estado em Brasília": {
      "Cnpj": "06.553.499/0003-02",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "CFLP - Compania Ferroviaria e de Logistica do Piaui": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "EMGERPI - Empresa de Gestão de Pessoas": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "PIFOMENTO - Agência de Fomento e Desenvolvimento do Estado do Piauí S.A.": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  },
  {
    "SIA - Secretaria de Inteligência Artificial, Economia Digital, Ciência, Tecnologia e Inovação": {
      "Cnpj": "",
      "Endereco": "Av. Pedro Freitas, 1900, Teresina, PI",
      "Telefone": ""
    }
  },
  {
    "MPPI - Ministério Público do Estado do Piauí": {
      "Cnpj": "",
      "Endereco": "",
      "Telefone": ""
    }
  }
]

# Modelo de Estado
class AppState(MessagesState):
    human_message: Optional[str]
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
    state["error"] = None
    state["human_message"] = None
    state["api_intent"] = None
    state["api_response"] = None

    system_prompt = f"""
        Você é um assistente especializado em classificação de intenções para o sistema SEAD, com capacidade de integrar dados via API.

        Siga estritamente estas diretrizes:

        1. LINGUAGEM:
        - Responda APENAS em português do Brasil
        - Use linguagem formal e técnica adequada para servidores públicos

        2. PROCESSAMENTO:
        - Analise a intenção com precisão antes de responder
        - Extraia parâmetros de forma minuciosa
        - Mantenha respostas curtas e objetivas (máximo 2 frases quando diretas)

        3. FORMATO DE SAÍDA:
        - Para classificações: APENAS JSON estruturado
        - Para respostas diretas: texto claro e conciso

        4. OPÇÕES DE INTENÇÃO:
        {{
        "pessoa": {{
            "descrição": "Consultar dados de servidor",
            "parâmetros": {{"nome": "Nome Completo ou Parcial"}},
            "exemplo": "Quem é Maria Souza? → {{"intent": "pessoa", "parameters": {{"nome": "Maria Souza"}}}}",
            "exemplo":"Qua o cargo de Ubaldo Junior → {{"intent": "pessoa", "parameters": {{"nome": "Maria Souza"}}}}"        
            }},
        "objetivo": {{
            "descrição": "Consultar objetivos institucionais",
            "parâmetros": {{"orgao": "Sigla ou Nome (Opcional)", "setor": "Sigla ou Nome (Opcional)"}},
            "exemplo": "Quais os objetivos da SEAD? → {{"intent": "objetivo", "parameters": {{"orgao": "SEAD"}}}}",
            "exemplo": "Qual o plano de governo da SEAD? → {{"intent": "objetivo", "parameters": {{"orgao": "SEAD"}}}}"
        }},
        "hierarquia": {{
            "descrição": "Estrutura organizacional",
            "parâmetros": {{"orgao": "Sigla ou Nome (Opcional)", "setor": "Sigla ou Nome (Opcional)"}},
            "exemplo": "Mostre a estrutura da SEAD → {{"intent": "hierarquia", "parameters": {{"orgao": "SEGOV"}}}}",
            "exemplo": "O que é a NTGD → {{"intent": "hierarquia", "parameters": {{"setor": "SEGOV"}}}}"
            "exemplo": "O que é SEAD → {{"intent": "hierarquia", "parameters": {{"orgao": "SEAD"}}}}",
        }},
        "outro": {{
            "descrição": "Demais assuntos",
            "response": None
        }}
        }}

        5. VALIDAÇÃO:
        - Confirme siglas antes de consultar (ex: "SEAD" ≠ "SED")
        - Para nomes incompletos, solicite complemento: "Poderia confirmar o nome completo?"
        - Em ambiguidades, enumere opções claras

        6. PERFORMANCE:
        - Priorize velocidade de resposta
        - Mantenha consistência terminológica
        - Documente eventuais limitações de dados

        **INSTRUÇÃO ADICIONAL PARA TODAS AS INTENÇÕES:**
        Considere como 'orgão' apenas se estiver na lista abaixo. Caso contrário, trate como 'setor' e use os dados da lista para complementar informações sobre orgão.

        Lista de órgãos válidos:
        {orgaos_validos}
        """
    
    try:
        state["human_message"] = state["messages"][-1].content
        response = requests.post(
            MANDU_API_URL,
            json={
                "model": "Qwen/Qwen3-30B-A3B",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": state["human_message"]}
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
        print(f"Chamando API para a intenção: {state["api_intent"]}")
        
    except Exception as e:
        print(f"Erro ao identificar intenção: {str(e)}")
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
                json={"orgao": params.get("orgao"), 
                      "setor": params.get("setor")},
                headers={"Content-Type": "application/json"},
                verify=False
            )
            state["api_response"] = response.json()
                    
    except Exception as e:
        print(f"Erro na API: {str(e)}")
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
    if state.get("error"):
        print(f"Erro detectado no estado: {state['error']}")
        state["message"] = "Desculpe, ocorreu um erro. Por favor, tente novamente."
        mensagem = parse_string_to_message(state["message"])
        state["messages"].append(mensagem)
        return state
    
    # passar a intenção, o contexto que o assistente conseguiu pesquisar (api_response), informações sobre orgão, instruções de responsta, explique que ele é o Chat Gestor desenvolvido pelo Nucleo .... com dados da aplicação Gestor

    system_prompt = f"""/no_think Você é um assistente do Chat para gestores desenvolvido pelo Nucleo de Tecnologia e Governo Digital (NTGD) da SEAD. Seu nome é Chat Gestor.

        Siga estritamente estas diretrizes:

        1. LINGUAGEM:
        - Responda APENAS em português do Brasil
        - Seja claro e conciso
        - Destaque informações principais
        - Use linguagem formal e técnica adequada para servidores públicos
        - Use formato de markdown
        - quando possivel enumere ou pontue informações em formato de lista ou pontos com markdown e pulando linhas

        2. PROCESSAMENTO:
        - Considere a intenção do usuario: {state.get("api_intent")}
        - Considere os seguintes dados, para enriquecer seu contexto de resposta: {state.get("api_response")}
        - Use a intenção do usuario em conjunto com os dados extraidos das ferramentas disponiveis (banco da aplicação Gestor) para orientar e melhorar sua resposta 

        **INSTRUÇÃO ADICIONAL:**
        Use os dados da lista para complementar informações sobre orgãos do Governo do Estado do Piaui caso necesario

        Lista de órgãos válidos:
        {orgaos_validos}
    """

    try:
        print("Enviando requisição para o MANDU_API_URL...")
        response = requests.post(
            MANDU_API_URL,
            json={
                "model": "Qwen/Qwen3-30B-A3B",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": state["human_message"]}
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