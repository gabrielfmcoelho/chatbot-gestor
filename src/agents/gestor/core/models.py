import re
from typing import Annotated, List, Literal, Union
from pydantic import BaseModel, Field, field_validator, HttpUrl

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