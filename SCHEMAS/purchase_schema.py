from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class PagamentoSchema(BaseModel):
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
    id_pagamento: int
    id_pedido: int
    id_cartao: Optional[int]
    chave_pix: Optional[str]
    valor: float
    numero_parcela: int
    data_pagamento: date

    model_config = ConfigDict(
        from_attributes=True,      
        extra="forbid",            
        validate_assignment=True,  
        str_strip_whitespace=True, 
        frozen=True,
    )