from pydantic import BaseModel, ConfigDict

class CartaoCadastro(BaseModel):
    numero_cartao: str
    nome_titular: str
    validade: str
    cvv: str
    
    model_config = ConfigDict(
        from_attributes=True
    )

class CartaoResponse(BaseModel):
    id_cartao: int
    numero_cartao: str
    nome_titular: str
    validade: str
    cvv: str
    
    model_config = ConfigDict(
        from_attributes=True
    )