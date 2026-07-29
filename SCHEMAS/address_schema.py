from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class EnderecoCompleto(BaseModel):

    rua: str
    bairro: str
    estado: str
    numero: str
    complemento: str
    cep: str

    model_config = ConfigDict(
            from_attributes=True,      
            extra="forbid",            
            validate_assignment=True,  
            str_strip_whitespace=True, 
            frozen=True,
        )

