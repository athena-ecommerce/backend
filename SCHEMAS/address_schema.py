from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class EnderecoCompleto(BaseModel):
    # Dados usados ao cadastrar um endereço; campos extras são rejeitados pela configuração abaixo.
    rua: str
    bairro: str
    estado: str
    numero: str
    complemento: Optional[str] = None
    cep: str

    model_config = ConfigDict(
            from_attributes=True,      
            extra="forbid",            
            validate_assignment=True,  
            str_strip_whitespace=True, 
            frozen=True,
        )


class EnderecoResponse(BaseModel):
    # Resposta com o identificador criado para permitir seleção e exclusão no checkout.
    id_endereco: int
    rua: str
    bairro: str
    estado: str
    numero: str
    complemento: Optional[str] = None
    cep: str


class EnderecoCepResponse(BaseModel):
    # Formato reduzido retornado pela consulta de CEP antes do usuário confirmar o endereço.
    rua: str
    bairro: str
    estado: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cep: str
