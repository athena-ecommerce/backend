from typing import List
from pydantic import BaseModel, ConfigDict, Field


class ItemCarrinhoAdicionar(BaseModel):

    id_produto: int
    quantidade: int = Field(gt=0, default=1)

    model_config = ConfigDict(
        extra="forbid",
    )


class ItemCarrinhoResposta(BaseModel):

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

    itens: List[ItemCarrinhoResposta]
    total: float
