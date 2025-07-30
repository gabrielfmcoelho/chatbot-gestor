from langgraph.graph import END, StateGraph



# Configuração do Grafo
Workflow = StateGraph(GestorState)

# Add nodes
#workflow.add_node("welcome", welcome_node)
Workflow.add_node("identify_intent", identify_intent)
Workflow.add_node("call_api", call_api)
Workflow.add_node("generate_response", generate_response)

# Set entry point
Workflow.set_entry_point("welcome")

# Add edges
Workflow.add_edge("welcome", "identify_intent")
Workflow.add_edge("identify_intent", "call_api")
Workflow.add_edge("call_api", "generate_response")

# End nodes
Workflow.add_edge("generate_response", END)

# Compile the workflow
gestor_agent = Workflow.compile()
gestor_agent.name = "gestor_agent"