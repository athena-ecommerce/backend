from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class UsuarioCadastro(BaseModel):

    nome_completo: str
    login: str
    senha: str
    data_nascimento: date
    cpf: str
    tipo_acesso: str

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )

class UsuarioCadastroResposta(BaseModel):

    nome_completo: str
    login: str
    data_nascimento: date
    cpf: str
    tipo_acesso: str

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )


class UsuarioLogin(BaseModel):

    login: str
    senha: str

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class TokenResposta(BaseModel):

    access_token: str
    token_type: str

    model_config = ConfigDict(
        extra="forbid",
    )