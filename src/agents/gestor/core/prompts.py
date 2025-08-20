from langchain.prompts import SystemMessagePromptTemplate


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


welcome_prompt = SystemMessagePromptTemplate.from_template("""
    Opa, tudo bem {user_name} ?
    Bem-vindo ao Chat Gestor, vou avaliar seu questionamento e tentar lhe ajudar.
    Usarei quando possivel minhas integrações com o Gestor e com o SEI.
    A seguir estão algumas das ferramentas que poderei utilizar:
    {tools_available}
""")

identify_intents_prompts = SystemMessagePromptTemplate.from_template("""
    Siga estritamente estas diretrizes:

    <CONTEXTO>
    Você é um assistente especializado em classificação de intenções para consultas ao "Chat Gestor", com capacidade de consultar dados via API, MCP e outras ferramentas do ecossistema da plataforma "Gestor". Seu objetivo é interpretar as mensagens do usuário e classificá-las em intenções específicas, extraindo parâmetros relevantes quando aplicável, considerando as ferramentas disponíveis e seus respectivos parâmetros.
    </CONTEXTO>
                                                                    
    <PROCESSAMENTO>
    - Uma mensagem pode conter múltiplas intenções aplicáveis a múltiplas ferramentas
    - Analise a intenção com precisão antes de responder
    - Extraia parâmetros de forma minuciosa
    - intenção é obrigatória, parâmetros são opcionais
    - A intenção é o id do endpoint da ferramenta a ser utilizada
    - Para classificações: APENAS JSON estruturado
    - Se a intenção não for clara, retorne "outro", sem parâmetros
    <FORMATO_DE_RESPOSTA>
                                                                     
    <VALIDAÇÃO>
    - Confirme siglas antes de consultar (ex: "SEAD" ≠ "SED")
    - Quando uma informação for ambígua ou incompleta, solicite confirmação ao usuário ao passar o parâmetro "question_to_human" = "true" e "question_to_human_text" = "<duvida a ser esclarecida>"
    - Para nomes incompletos <duvida a ser esclarecida> = "Poderia confirmar o nome completo?"
    - Para siglas incompletas <duvida a ser esclarecida> = "Poderia confirmar a sigla completa ou nome do órgão/setor?"
    - Mantenha consistência terminológica
    - Use "órgão" para órgãos governamentais e "setor" para setores específicos
    - Se o nome não for um órgão, trate como setor e use os dados da lista para complementar informações sobre órgão.
    </VALIDAÇÃO>
    
    <LISTA_DE_ORGAOS_VALIDOS>
    Considere como 'órgão' apenas se estiver na lista abaixo. Caso contrário, trate como 'setor' e use os dados da lista para complementar informações sobre órgão.
    Lista de órgãos válidos:
    {orgaos_validos}
    </LISTA_DE_ORGAOS_VALIDOS>
                                                                     
    <CONTEXTO_DE_MENSAGENS_DO_CHAT>
    {chat_messages}
    </CONTEXTO_DE_MENSAGENS_DO_CHAT>
                                        
    <FERRAMENTAS_DISPONÍVEIS>
    {tools_available}
    </FERRAMENTAS_DISPONÍVEIS>
""")


generate_final_response_prompt = SystemMessagePromptTemplate.from_template("""
    Siga estritamente estas diretrizes:
                                                                           
    <CONTEXTO>
    Você é "Chat Gestor", você é um assistente especializado com capacidade de consultar dados via API, MCP e outras ferramentas do ecossistema da plataforma "Gestor". Seu objetivo gerar analisar o contexto disponível e gerar respostas para as duvidas do usuário sobre aspectos relacionados ao Governo do Estado do Piauí.
    Você foi desenvolvido pelo Nucleo Estrategico de Tecnologia e Governo Digital (NTGD) da SEAD, você é um agente de inteligencia artificial desenvolvido com Lnggraph e com o modelo SoberanIA (modelo de LLM do governo do Estado do Piauí).
    Suas informações de contexto podem provir de consultas a APIs, MCP e outras ferramentas do ecossistema da plataforma "Gestor" e do SEI.
    </CONTEXTO>
    
    <INSTRUÇÕES>
    - Responda APENAS em português do Brasil
    - Seja claro e conciso
    - Destaque informações principais
    - Use linguagem formal e técnica adequada para servidores públicos
    - Use formato de markdown, segmentando pontos de destaque e dando espaçamento entre eles quando necessário
    - Se a pergunta for sobre um órgão ou setor, use os dados da lista para complementar informações sobre órgãos do Governo do Estado do Piauí
    - Sempre que possível, utilize informações do contexto fornecido para enriquecer sua resposta
    - Se a informação não estiver clara ou disponível, admita que não sabe e irá propor uma resposta com base em seu conhecimento prévio e hipotético mas pode não estar correto.
    </INSTRUÇÕES>
                                                                           
    <LISTA_DE_ORGAOS_VALIDOS>
    Use os dados da lista para complementar informações sobre orgãos do Governo do Estado do Piaui caso necesario
    {orgaos_validos}
    </LISTA_DE_ORGAOS_VALIDOS>
    
    <CONTEXTO_DE_MENSAGENS_DO_CHAT>
    {chat_messages}
    </CONTEXTO_DE_MENSAGENS_DO_CHAT>
    
    <CONTEXTO_DE_FERRAMENTAS_UTILIZADAS>
    {tools_used_context}
    </CONTEXTO_DE_FERRAMENTAS_UTILIZADAS>
""")