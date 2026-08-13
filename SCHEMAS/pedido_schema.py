from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from SCHEMAS.address_schema import EnderecoCompleto
from SCHEMAS.produtos_schema import ArteCadastro
from SCHEMAS.pedido_produto_schema import PedidosProdutosSchema

class PedidoCompleto(BaseModel):
    # Reúne endereço, total e produtos para transformar o checkout em um pedido.
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
    # Formato detalhado usado na página de histórico de compras.
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
    # Resposta curta após a criação, suficiente para acompanhar o pedido.
    id_pedido: int
    valor_total: float
    data_pedido: datetime
    status: str

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )
