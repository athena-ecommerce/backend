from pydantic import BaseModel, ConfigDict, Field


class ArteCadastro(BaseModel):

    nome: str
    tipo_arte: str
    preco: float = Field(gt=0)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class ArteAtualizar(BaseModel):

    nome: str
    tipo_arte: str
    preco: float = Field(gt=0)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class ArteResposta(BaseModel):

    id_produto: int
    nome: str
    tipo_arte: str
    preco: float
    id_usuario: int

    model_config = ConfigDict(
        from_attributes=True,
    )
