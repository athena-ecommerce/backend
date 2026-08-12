from pydantic import BaseModel, ConfigDict


class PedidosProdutosSchema(BaseModel):
    id_produto: int
    quantidade: int

    model_config = ConfigDict(
        from_attributes=True
    )