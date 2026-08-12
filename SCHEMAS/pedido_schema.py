from pydantic import BaseModel, ConfigDict
from datetime import datetime
from SCHEMAS.address_schema import EnderecoCompleto
from SCHEMAS.produtos_schema import ArteCadastro
from SCHEMAS.pedido_produto_schema import PedidosProdutosSchema, PedidoProdutoResponse

class PedidoCompleto(BaseModel):
    valor_total: float
    id_endereco: int
    produtos: list[PedidosProdutosSchema]

    model_config = ConfigDict(
        from_attributes=True,
    )

class PedidoCompletoResposta(BaseModel):
    valor_total: float
    data_pedido: datetime
    status: str
    endereco: EnderecoCompleto
    produtos: list[ArteCadastro]

    model_config = ConfigDict(
        from_attributes=True,
    )

class PedidoResponse(BaseModel):
    id_pedido: int
    id_usuario: int
    id_endereco: int
    valor_total: float
    status: str
    produtos: list[PedidoProdutoResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )


class ListaPedidosResponse(BaseModel):
    pedidos: list[PedidoResponse]

    model_config = ConfigDict(from_attributes=True)