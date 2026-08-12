from pydantic import BaseModel, ConfigDict
from datetime import date
from SCHEMAS.address_schema import EnderecoCompleto
from SCHEMAS.produtos_schema import ArteCadastro
from SCHEMAS.pedido_produto_schema import PedidosProdutosSchema

class PedidoCompleto(BaseModel):
    valor_total: float
    id_endereco: int
    produtos: list[PedidosProdutosSchema]

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

class PedidoResponse(BaseModel):
    id_pedido: int
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
