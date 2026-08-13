from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import date

class UsuarioCadastro(BaseModel):
    # Entrada da criação de conta, incluindo o perfil escolhido pelo usuário.

    nome_completo: str
    login: EmailStr
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
    # Retorna os dados públicos da conta sem expor a senha.

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
    # Credenciais mínimas necessárias para iniciar uma sessão.

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
    # A API devolve os dois tokens usados para manter e renovar o acesso.

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
    # Primeiro passo da recuperação: identificar a conta pelo e-mail.

    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )

class RecuperarSenhaCodigo(BaseModel):
    # Confirma o código recebido junto da conta que solicitou a recuperação.

    email: EmailStr
    codigo: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )

class RecuperarSenhaNovaSenha(BaseModel):
    # Payload final da recuperação, validado novamente antes de salvar a nova senha.

    senha: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=True,
    )
