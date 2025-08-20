from langgraph.graph import END, StateGraph

from agents.gestor.flows.mcp import (
    welcome_node,
    identify_intents,
    execute_tools,
    generate_final_response
)

from agents.gestor.core.states import GestorState



# Configuração do Grafo
Workflow = StateGraph(GestorState)

# Conditional routing function
def should_execute_tools(state: GestorState) -> str:
    """Route to tools if tool calls are pending, otherwise go to final response."""
    if state.get("tool_calls_pending", False):
        return "execute_tools"
    return "generate_final_response"

# Add nodes
Workflow.add_node("welcome", welcome_node)
Workflow.add_node("identify_intents", identify_intents)
Workflow.add_node("execute_tools", execute_tools)
Workflow.add_node("generate_final_response", generate_final_response)

# Set entry point
Workflow.set_entry_point("welcome")

# Add edges
Workflow.add_edge("welcome", "identify_intents")
Workflow.add_conditional_edges(
    "identify_intents",
    should_execute_tools,
    {
        "execute_tools": "execute_tools",
        "generate_final_response": "generate_final_response"
    }
)
Workflow.add_edge("execute_tools", "generate_final_response")

# End nodes
Workflow.add_edge("generate_final_response", END)

# Compile the Workflow
gestor_agent = Workflow.compile()
gestor_agent.name = "gestor_agent"