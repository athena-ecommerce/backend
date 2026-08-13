from pydantic import BaseModel, ConfigDict


class PedidosProdutosSchema(BaseModel):
    # Representa a quantidade de uma obra dentro de um pedido específico.
    id_produto: int
    quantidade: int

    model_config = ConfigDict(
        from_attributes=True
    )
