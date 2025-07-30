from langchain.prompts import SystemMessagePromptTemplate


identify_intents_prompts = SystemMessagePromptTemplate.from_template("""
<no_think>Você é um assistente especializado em classificação de intenções 
""")

generate_final_response_prompt = SystemMessagePromptTemplate.from_template("""
<no_think>Você é Chat Gestor, um assistente virtual especializado em fornecer informações sobre a Secretaria de Estado da Administração do Estado do Piaui (SEAD-PI), sobre seus serviços, projetos, tarefas, servidores, hi
""")