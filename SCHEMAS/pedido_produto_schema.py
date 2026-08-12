from pydantic import BaseModel, ConfigDict
from SCHEMAS.produtos_schema import ProdutoResponse


class PedidosProdutosSchema(BaseModel):
    id_produto: int
    quantidade: int

    model_config = ConfigDict(
        from_attributes=True
    )


class PedidoProdutoResponse(BaseModel):
    quantidade: int
    produto: ProdutoResponse

    model_config = ConfigDict(from_attributes=True)