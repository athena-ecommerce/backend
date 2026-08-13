from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class CartaoCadastro(BaseModel):
    # Valida o formato básico do cartão antes de qualquer tentativa de persistência.
    numero_cartao: str = Field(pattern=r"^\d{16}$")
    nome_titular: str = Field(min_length=3, max_length=100)
    validade: str = Field(pattern=r"^(0[1-9]|1[0-2])/\d{2}$")
    cvv: str = Field(pattern=r"^\d{3}$")
    tipo: Literal["CREDITO", "DEBITO"]
    
    model_config = ConfigDict(
        from_attributes=True
    )

class CartaoResponse(BaseModel):
    # A resposta usa apenas os dados seguros e os últimos dígitos do cartão.
    id_cartao: int
    nome_titular: str
    validade: str
    tipo: str
    final_cartao: str
    
    model_config = ConfigDict(
        from_attributes=True
    )
