from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile, File, Form

class ArteCadastro(BaseModel):

    nome: str
    tipo_arte: str
    preco: float = Field(gt=0)
    imagem: UploadFile

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @classmethod
    def as_form(
        cls,
        nome: str = Form(...),
        tipo_arte: str = Form(...),
        preco: float = Form(...),
        imagem: UploadFile = File(...),
    ):
        return cls(
            nome=nome,
            tipo_arte=tipo_arte,
            preco=preco,
            imagem=imagem,
        )

class ArteAtualizar(BaseModel):

    nome: str
    tipo_arte: str
    preco: float = Field(gt=0)
    imagem: UploadFile

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @classmethod
    def as_form(
        cls,
        nome: str = Form(...),
        tipo_arte: str = Form(...),
        preco: float = Form(...),
        imagem: UploadFile = File(...),
    ):
        return cls(
            nome=nome,
            tipo_arte=tipo_arte,
            preco=preco,
            imagem=imagem,
        )

class ImagensQuadrosResposta(BaseModel):

    id_imagem_quadro: int
    imagem: str
    imagem_public_id: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class ArteResposta(BaseModel):

    id_produto: int
    nome: str
    tipo_arte: str
    preco: float
    id_usuario: int
    imagem: ImagensQuadrosResposta

    model_config = ConfigDict(
        from_attributes=True,
    )
