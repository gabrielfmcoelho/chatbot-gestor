import re
from typing import Annotated, List, Literal, Union
from pydantic import BaseModel, Field, field_validator, HttpUrl

class IntentBase(BaseModel):
    intent: str = Field(..., description="ID da tool ou endpoint a ser utilizado")
    parameters: Union[dict, None] = Field(
        default=None, description="Parâmetros adicionais para a intenção"
    )
    question_to_human: bool = Field(
        default=False, description="Indica se a intenção requer confirmação do usuário"
    )
    question_to_human_text: Union[str, None] = Field(
        default=None, description="Texto da pergunta a ser feita ao usuário se question_to_human for True"
    )
    api_response: Union[dict, None] = Field(
        default=None, description="Resposta da API ou ferramenta utilizada"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "consultar_servidor",
                "parameters": {
                    "nome": "João da Silva",
                    "sigla_orgao": "SEAD"
                },
                "question_to_human": True,
                "question_to_human_text": "Poderia confirmar o nome completo?"
            }
        }

    @field_validator("parameters", mode="before")
    def validate_parameters(cls, value: Union[dict, None]) -> Union[dict, None]:
        if isinstance(value, dict):
            return {k: v for k, v in value.items() if v is not None}
        return value
    
    @field_validator("question_to_human_text", mode="before")
    def validate_question_to_human_text(cls, value: Union[str, None]) -> Union[str, None]:
        if value is not None and not isinstance(value, str):
            raise ValueError("question_to_human_text must be a string")
        return value.strip() if value else None

    @field_validator("intent")
    def validate_intent(cls, value: str) -> str:
        if not value:
            raise ValueError("Intent cannot be empty")
        return value.strip().lower()
    
class IntentClassification(BaseModel):
    """
    Modelo para classificar intenções de usuário.
    """
    intents: List[IntentBase] = Field(
        ...,
        description="Lista de intenções identificadas na mensagem do usuário"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "intents": [
                    {
                        "intent": "consultar_servidor",
                        "parameters": {
                            "nome": "João da Silva",
                            "sigla_orgao": "SEAD"
                        },
                        "question_to_human": True,
                        "question_to_human_text": "Poderia confirmar o nome completo?"
                    }
                ]
            }
        }

    @field_validator("intents")
    def validate_intents(cls, value: List[IntentBase]) -> List[IntentBase]:
        if not value:
            raise ValueError("At least one intent must be provided")
        return value
    

# ===== UTILITY VALIDATORS =====

def validate_and_transform_protocol_code(protocol_code_to_evaluate: str) -> str:
    # protocol has the pattern of XXXXX.XXXXXX/YYYY-XX, X ARE ONLY DIGITS
    # IF THE PROCOTOL HAS THE PATTERN XXXXXXXXXXXYYYYXX TRANSFORM TO XXXXX.XXXXXX/YYYY-XX
    # IF THE code does not have the match than raise invalid protocol format
    pass


def verify_if_is_orgao(name: str) -> bool:
    # verify if name is in: [SEAD, SEGOV, MPPI, SSP, SESAPI, SEPLAN, SEFAZ]
    pass


def validate_email_address(email: str) -> str:
    """Validate email address format using basic regex."""
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValueError('Invalid email address format')
    
    return email.lower()