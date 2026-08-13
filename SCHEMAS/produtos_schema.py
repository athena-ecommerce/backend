from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile, File, Form

class ArteCadastro(BaseModel):
    # Dados da obra e do arquivo que serão recebidos no multipart do cadastro.

    nome: str
    tipo_arte: str
    preco: float = Field(gt=0)
    descricao: str
    imagem: UploadFile
    descricao_foto: str
    dimensoes: str

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
        descricao: str = Form(...),
        imagem: UploadFile = File(...),
        descricao_foto: str = Form(...),
        dimensoes: str = Form(...),
    ):
        # Converte campos multipart em um objeto Pydantic para manter a validação centralizada.
        return cls(
            nome=nome,
            tipo_arte=tipo_arte,
            preco=preco,
            descricao=descricao,
            imagem=imagem,
            descricao_foto=descricao_foto,
            dimensoes=dimensoes
        )

class ArteAtualizar(BaseModel):
    # Reaproveita o mesmo contrato do cadastro, mas aplicado a uma obra já existente.

    nome: str
    tipo_arte: str
    preco: float = Field(gt=0)
    descricao: str
    imagem: UploadFile
    descricao_foto: str
    dimensoes: str

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
        descricao: str = Form(...),
        imagem: UploadFile = File(...),
        descricao_foto: str = Form(...),
        dimensoes: str = Form(...),
    ):
        # O formulário de edição chega separado, então precisa ser remontado antes da validação.
        return cls(
            nome=nome,
            tipo_arte=tipo_arte,
            preco=preco,
            descricao=descricao,
            imagem=imagem,
            descricao_foto=descricao_foto,
            dimensoes=dimensoes
        )

class ImagensQuadrosResposta(BaseModel):
    # Metadados da imagem armazenada externamente e vinculada à obra.

    id_imagem_quadro: int
    imagem: str
    imagem_public_id: str
    descricao_foto: str
    dimensoes: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class ArteResposta(BaseModel):
    # Resposta pública de uma obra com sua imagem e o artista responsável.

    id_produto: int
    nome: str
    tipo_arte: str
    preco: float
    id_usuario: int
    descricao: str
    imagem: ImagensQuadrosResposta

    model_config = ConfigDict(
        from_attributes=True,
    )
