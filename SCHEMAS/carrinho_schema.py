from typing import List
from pydantic import BaseModel, ConfigDict, Field


class ItemCarrinhoAdicionar(BaseModel):
    # A quantidade precisa ser positiva para não corromper o total do carrinho.

    id_produto: int
    quantidade: int = Field(gt=0, default=1)

    model_config = ConfigDict(
        extra="forbid",
    )


class ItemCarrinhoResposta(BaseModel):
    # Inclui os dados já enriquecidos do produto para a tela não precisar fazer outra busca.

    id_produto: int
    nome: str
    preco: float
    quantidade: int
    subtotal: float
    id_usuario: int
    autor: str
    imagem: str
    alt: str
    dimensoes: str


class CarrinhoResposta(BaseModel):
    # Contrato único usado tanto ao consultar quanto ao alterar o carrinho.

    itens: List[ItemCarrinhoResposta]
    total: float
