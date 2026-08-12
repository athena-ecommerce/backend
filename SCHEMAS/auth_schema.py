from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

# Os schemas deixam explícito o contrato de entrada e saída da autenticação.
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
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )

class UsuarioLoginResposta(BaseModel):

    login: str
    access_token: str
    refresh_token: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )

class RecuperarSenha(BaseModel):

    email: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )

class RecuperarSenhaCodigo(BaseModel):

    email: str
    codigo: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )

class RecuperarSenhaNovaSenha(BaseModel):

    senha: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )
