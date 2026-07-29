from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from MODELS import Produtos
from SCHEMAS.address_schema import EnderecoCompleto
from SCHEMAS.produtos_schema import ArteCadastro

class PedidoCompleto(BaseModel):

    valor_total: float
    id_endereco: int
    ids_produto: list[int]

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )

class PedidoCompletoResposta(BaseModel):

    valor_total: float
    data_pedido: date
    status: str
    endereco: EnderecoCompleto
    produtos: list[ArteCadastro]

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )

