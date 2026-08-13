from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional
from datetime import datetime

from SCHEMAS.pedido_produto_schema import PedidosProdutosSchema

class PagamentoSchema(BaseModel):
    # Define qual método foi escolhido e os valores que serão registrados na transação.
    id_pedido: int
    id_cartao: Optional[int]
    chave_pix: Optional[str]
    valor: float
    numero_parcelas: int
    
    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )


class PagamentoResponse(BaseModel):
    # Retorna o comprovante básico do pagamento sem dados sensíveis do cartão.
    id_pagamento: int
    id_pedido: int
    id_cartao: Optional[int]
    chave_pix: Optional[str]
    valor: float
    numero_parcela: int
    data_pagamento: datetime

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )


class PagamentoCartaoCompleto(BaseModel):
    # Modelo usado quando o checkout envia um cartão novo junto dos dados do pedido.
    id_endereco: int
    valor_total: float = Field(gt=0)
    produtos: list[PedidosProdutosSchema] = Field(min_length=1)
    numero_cartao: str = Field(pattern=r"^\d{16}$")
    nome_titular: str = Field(min_length=3, max_length=100)
    validade: str = Field(pattern=r"^(0[1-9]|1[0-2])/\d{2}$")
    cvv: str = Field(pattern=r"^\d{3}$")
    tipo: Literal["CREDITO", "DEBITO"]
    numero_parcelas: int = Field(ge=1, le=12)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PagamentoCartaoCompletoResposta(BaseModel):
    id_pedido: int
    id_pagamento: int
    status: str
