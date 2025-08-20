import logging
import json

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from core.llm import get_model
from core.llm import get_configured_model
from core import settings

from agents.gestor.core.tools import get_tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage

from agents.gestor.core.prompts import (
    welcome_prompt,
    identify_intents_prompts,
    generate_final_response_prompt,
    orgaos_validos
)

from agents.gestor.core.models import IntentClassification

from agents.gestor.core.states import GestorState
from agents.gestor.core.utils import (
    wrap_model,
    get_last_user_message,
    _prepare_messages,
    build_conversation_context,
    generate_tool_call_id,
    summarize_large_response,
    manage_context_size,
    is_response_too_large,
    clean_state_for_serialization
)


logger = logging.getLogger(__name__)

MANDU_API_URL = "https://api.sobdemanda.mandu.piaui.pro/v1/chat/completions"
MANDU_API_KEY = "sk-ZfNzJZFOmJHVDnlOfnOugCivU4IL5orM"

async def check_if_intents_available(state: GestorState, config: RunnableConfig):
    print("-> check_if_intents_available")
    print(state)
    try:
        intents = state.get("intents")
        if intents is None:
            logger.info("[check_if_intents_available] No intents found, continuing...")
            return None
            
        # Check if intents has the expected structure
        if hasattr(intents, 'intents') and any(
            intent.get("question_to_human", False) for intent in intents.intents
        ):
            question_text = next(
                (intent["question_to_human_text"] for intent in intents.intents if intent.get("question_to_human", False)), 
                "Poderia esclarecer sua dúvida?"
            )
            logger.info(f"[identify_intents] Interrompendo o fluxo para perguntar ao usuário: {question_text}")
            user_input = interrupt(question_text)
            state["messages"].append(HumanMessage(content=user_input))
            return await identify_intents(state, config)
    except Exception as e:
        logger.error(f"[check_if_intents_available] Erro ao verificar intenções: {e}")
        return None

async def check_tool_availability_and_interrupt(state: GestorState, config: RunnableConfig, tools_available: list):
    """
    Check if we have appropriate tools for the user's request.
    If not, interrupt to ask for more information.
    """
    try:
        last_user_message = get_last_user_message(state)
        
        # If no tools available and user seems to be asking for specific information
        if not tools_available and last_user_message:
            # Keywords that might indicate the user needs specific tools
            info_keywords = ["consultar", "buscar", "verificar", "informações", "dados", "relatório", "status"]
            
            if any(keyword in last_user_message.lower() for keyword in info_keywords):
                question_text = ("Não encontrei ferramentas disponíveis para sua consulta. "
                               "Poderia fornecer mais detalhes sobre o que você gostaria de consultar? "
                               "Por exemplo: número de protocolo, CPF, CNPJ, ou tipo específico de informação.")
                
                logger.info(f"[tool_availability_check] Interrompendo por falta de ferramentas adequadas: {question_text}")
                user_input = interrupt(question_text)
                state["messages"].append(HumanMessage(content=user_input))
                return True  # Indicates we need to re-process
        
        return False  # No interruption needed
        
    except Exception as e:
        logger.error(f"[check_tool_availability_and_interrupt] Erro: {e}")
        return False

async def welcome_node(state: GestorState, config: RunnableConfig) -> GestorState:
    """
    Node to welcome the user and initialize the state.
    """
    print("--> welcome_node")
    if not state.get("first_run", True):
        logger.info("[welcome_node] Iniciando o fluxo de boas-vindas.")
        state["first_run"] = False
        response = welcome_prompt.format(user_name=config.get("user_name", "Ubaldo Junior"))
        return clean_state_for_serialization({"messages": [AIMessage(content=response)]})

async def identify_intents(state: GestorState, config: RunnableConfig) -> GestorState:
    """
    Node to identify the user's intent based on the messages.
    """
    print("--> identify_intents")
    try:
        logger.info("[identify_intent] Identificando a intenção do usuário.")

        configurable = config.get("configurable", {})

        print(f"intents: {state.get('intents')}")

        # if intent[0] == "outro" or intents is None or some intent has "question_to_human" set to true, interrupt the flow and use attribute question_to_human_text as text to ask the user with interrupt pattern
        await check_if_intents_available(state, config)
        print("interrupt check completed.")
        tools_available = await get_tools(state)
        
        # Check if we need to interrupt due to lack of appropriate tools
        if await check_tool_availability_and_interrupt(state, config, tools_available):
            # Re-run the intent identification with the new user input
            return await identify_intents(state, config)
        
        #tools_available_str = ", ".join([tool.name for tool in tools_available]) if tools_available else "Nenhuma ferramenta disponível"
        
        #system_prompt = identify_intents_prompts.format(
        #    intent_model=IntentClassification.model_json_schema(),
        #    orgaos_validos=orgaos_validos,
        #    chat_messages=build_conversation_context(state),
        #    tools_available=tools_available_str,
        #)
        #print("System prompt prepared for intent identification.")

        model_name = configurable.get("model", settings.DEFAULT_MODEL)
        print(f"Using model: {model_name}")

        m = get_model(model_name)
        print(f"Model {model_name} retrieved, {type(m)}")
        m_with_bind_tools = m.bind_tools(tools_available)
        print("Model bound with tools.")

        model_runnable = wrap_model(
            m_with_bind_tools,
            #m_with_bind_tools.with_structured_output(IntentClassification),
            system_prompt="voce é um assistente inteligente"
        ).with_config(tags=["skip_stream"])
        print("Model runnable created with tools and system prompt.")
        
        print("Invoking model to identify intents...")
        response = await model_runnable.ainvoke(state, config)
        print("Response received from model.")
        print(f"[identify_intents] Resposta do modelo: {response}")

        # Check if model made tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"[identify_intents] Tool calls detected: {response.tool_calls}")
            # Add the AI message with tool calls to state
            state["messages"].append(response)
            cleaned_state = clean_state_for_serialization({"messages": state["messages"], "tool_calls_pending": True})
            return cleaned_state
        elif isinstance(response, IntentClassification):
            state["intents"] = response
            logger.info(f"[identify_intents] Intenções identificadas: {response}")
            return clean_state_for_serialization(state)
        else:
            logger.error(f"[identify_intents] Resposta do modelo não é do tipo IntentClassification: {response}")
            return clean_state_for_serialization({"messages": [AIMessage(content="Desculpe, não consegui identificar sua intenção.")]})
    except Exception as e:
        logger.error(f"[identify_intents] Erro ao identificar intenções: {e}")
        return clean_state_for_serialization({"messages": [AIMessage(content="Desculpe, ocorreu um erro ao identificar sua intenção.")]})
        


async def execute_tools(state: GestorState, config: RunnableConfig) -> GestorState:
    """
    Node to execute tool calls when the model requests them.
    """
    print("--> execute_tools")
    try:
        logger.info("[execute_tools] Starting tool execution...")
        
        # Get the last message which should contain tool calls
        last_message = state["messages"][-1]
        print(f"Last message type: {type(last_message)}")
        print(f"Last message: {last_message}")
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            print("No tool calls found in last message")
            return state
        
        print(f"Found {len(last_message.tool_calls)} tool calls")
        
        # Get tools for execution
        print("Fetching tools for execution...")
        tools_available = await get_tools(state)
        print(f"Retrieved {len(tools_available)} tools for execution")
        
        # Create a mapping of tool names to tool functions
        tools_map = {tool.name: tool for tool in tools_available}
        print(f"Available tool names: {list(tools_map.keys())}")
        
        # Initialize executed_tool_calls if not present
        if "executed_tool_calls" not in state:
            state["executed_tool_calls"] = []
        
        # Execute each tool call manually
        tool_results = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            # Generate a unique ID to prevent duplicate execution
            unique_call_id = generate_tool_call_id(tool_name, tool_args)
            
            # Check if this tool call was already executed
            if unique_call_id in state.get("executed_tool_calls", []):
                print(f"Skipping duplicate tool call: {tool_name} with args: {tool_args}")
                continue
            
            print(f"Executing tool: {tool_name} with args: {tool_args}")
            
            if tool_name in tools_map:
                try:
                    tool = tools_map[tool_name]
                    print(f"Found tool: {tool}")
                    print(f"Tool type: {type(tool)}")
                    
                    # Execute the tool
                    if hasattr(tool, 'ainvoke'):
                        result = await tool.ainvoke(tool_args)
                    elif hasattr(tool, 'invoke'):
                        result = tool.invoke(tool_args)
                    else:
                        result = await tool(**tool_args)
                    
                    print(f"Tool {tool_name} executed successfully. Result length: {len(str(result))}")
                    
                    # Handle large responses
                    result_str = str(result)
                    if is_response_too_large(result_str):
                        logger.info(f"Large response detected for {tool_name}, summarizing...")
                        result_str = summarize_large_response(result_str, tool_name)
                    
                    # Create tool message
                    tool_message = ToolMessage(
                        content=result_str,
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                    tool_results.append(tool_message)
                    
                    # Mark this tool call as executed
                    state["executed_tool_calls"].append(unique_call_id)
                    
                except Exception as tool_error:
                    print(f"Error executing tool {tool_name}: {tool_error}")
                    import traceback
                    traceback.print_exc()
                    
                    # Create error message
                    tool_message = ToolMessage(
                        content=f"Error executing {tool_name}: {str(tool_error)}",
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                    tool_results.append(tool_message)
            else:
                print(f"Tool {tool_name} not found in available tools")
                tool_message = ToolMessage(
                    content=f"Tool {tool_name} not found",
                    tool_call_id=tool_id,
                    name=tool_name
                )
                tool_results.append(tool_message)
        
        # Add tool results to state
        state["messages"].extend(tool_results)
        
        # Clear the tool_calls_pending flag
        state["tool_calls_pending"] = False
        
        # Manage context size to prevent overflow
        state = manage_context_size(state)
        
        # Clean state to ensure serialization compatibility
        state = clean_state_for_serialization(state)
        
        print(f"Tool execution completed. Added {len(tool_results)} tool messages")
        print(f"Final state messages count: {len(state.get('messages', []))}")
        
        return state
        
    except Exception as e:
        print(f"Error in execute_tools: {e}")
        logger.error(f"[execute_tools] Error executing tools: {e}")
        import traceback
        traceback.print_exc()
        return clean_state_for_serialization({"messages": [AIMessage(content="Desculpe, ocorreu um erro ao executar as ferramentas.")]})


async def generate_final_response(state: GestorState, config: RunnableConfig) -> GestorState:
    """
    Node to generate the final response based on the tool results.
    """
    print("--> generate_final_response")
    logger.info("[generate_final_response] Gerando a resposta final.")

    configurable = config.get("configurable", {})
    
    # Look for tool results in the conversation
    tool_results = []
    for message in state.get("messages", []):
        if hasattr(message, '__class__') and message.__class__.__name__ == 'ToolMessage':
            tool_results.append({
                "tool_name": message.name,
                "result": message.content
            })
    
    print(f"Found {len(tool_results)} tool results")
    
    # Build context from tool results
    tools_used_context = ""
    if tool_results:
        for tool_result in tool_results:
            tools_used_context += f"Ferramenta: {tool_result['tool_name']}, Resposta: {tool_result['result']}\n"
        print(f"Tools context: {tools_used_context}")
    else:
        # If no tool results, check if we have conversation context
        last_user_message = None
        for message in reversed(state.get("messages", [])):
            if hasattr(message, '__class__') and message.__class__.__name__ == 'HumanMessage':
                last_user_message = message.content
                break
        
        if last_user_message:
            tools_used_context = f"Pergunta do usuário: {last_user_message}"
            print(f"No tool results, using user question: {last_user_message}")
        else:
            logger.error("[generate_final_response] Nenhum resultado de ferramenta ou pergunta encontrada.")
            return {"messages": [AIMessage(content="Desculpe, não consegui processar sua solicitação.")]}

    system_prompt = generate_final_response_prompt.format(
        orgaos_validos=orgaos_validos,
        chat_messages=build_conversation_context(state),
        tools_used_context=tools_used_context
    )
    
    print("System prompt prepared for final response")

    model_name = configurable.get("model", settings.DEFAULT_MODEL)
    m = get_model(model_name)
    model_runnable = wrap_model(
        m, 
        system_prompt=system_prompt
    )
    
    print("Invoking model for final response...")
    response = await model_runnable.ainvoke(state, config)
    print(f"Final response received: {response}")
    logger.info(f"[generate_final_response] Resposta do modelo: {response}")
    
    # Handle different response types
    if isinstance(response, AIMessage):
        state["messages"].append(response)
        return clean_state_for_serialization(state)
    elif isinstance(response, str):
        # If the model returns a string, wrap it in an AIMessage
        ai_message = AIMessage(content=response)
        state["messages"].append(ai_message)
        return clean_state_for_serialization(state)
    else:
        logger.error(f"[generate_final_response] Resposta do modelo tipo inesperado: {type(response)} - {response}")
        # Try to convert to string and wrap in AIMessage
        try:
            content = str(response) if response else "Desculpe, não consegui gerar uma resposta adequada."
            ai_message = AIMessage(content=content)
            state["messages"].append(ai_message)
            return clean_state_for_serialization(state)
        except Exception as e:
            logger.error(f"[generate_final_response] Erro ao processar resposta: {e}")
            return clean_state_for_serialization({"messages": [AIMessage(content="Desculpe, não consegui gerar uma resposta adequada.")]})

