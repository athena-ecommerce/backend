from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from DEPENDENCIES import pegar_sessao, verificar_token
from MODELS import Produtos, Usuarios, Imagens_Quadros
from SCHEMAS import ArteAtualizar, ArteCadastro, ArteResposta

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

arts_router = APIRouter(prefix="/arts", tags=["Artes"])

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def buscar_arte_http(id_produto: int, db: Session) -> Produtos:
    arte = db.get(Produtos, id_produto)

    if not arte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arte não encontrada",
        )

    return arte

def buscar_imagem_arte_http(id_produto: int, db: Session) -> Imagens_Quadros:
    imagem = db.scalar(select(Imagens_Quadros).where(Imagens_Quadros.id_produto == id_produto).limit(1))

    if not imagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imagem da arte não encontrada",
        )

    return imagem

def validar_dono_da_arte(arte: Produtos, usuario: Usuarios):
    if arte.id_usuario != usuario.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Essa arte não pertence a você",
        )

def cadastrar_imagem(imagem: UploadFile):
    resultado = cloudinary.uploader.upload(
        imagem.file,
        resource_type="image"
    )

    url = resultado["secure_url"]
    public_id = resultado["public_id"]

    return [url, public_id]

def atualizar_imagem(imagem: UploadFile, public_id_antigo: str):

    resultado = cloudinary.uploader.upload(
        imagem.file,
        public_id=public_id_antigo,
        overwrite=True,
        invalidate=True,
        resource_type="image",
    )

    url = resultado["secure_url"]
    public_id = resultado["public_id"]

    return [url, public_id]

def deletar_imagem(public_id: str):
    resultado = cloudinary.uploader.destroy(
        public_id,
        invalidate=True,
    )

    if resultado.get("result") != "ok":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Esse quadro não foi encontrado!",
        )

def montar_dicionario_resposta(arte: Pedido, imagem_arte: Imagens_Quadros):
    return  {
        "id_produto": arte.id_produto,
        "nome": arte.nome,
        "tipo_arte": arte.tipo_arte,
        "preco": arte.preco,
        "id_usuario": arte.id_usuario,
        "imagem": imagem_arte,
    }

@arts_router.get("/", response_model=List[ArteResposta])
async def listar_artes(
    db: Session = Depends(pegar_sessao),
    tipo_arte: Optional[str] = Query(None, description="Filtra pela categoria/tipo da arte"),
    nome: Optional[str] = Query(None, description="Busca pelo nome da arte"),
    preco_min: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    preco_max: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    ordenar_por: Optional[str] = Query(
        None, description="Valores aceitos: nome, preco-menor, preco-maior"
    ),
):
    stmt = (
        select(Produtos, Imagens_Quadros)
        .join(
            Imagens_Quadros,
            Produtos.id_produto == Imagens_Quadros.id_produto
        )
    )

    if tipo_arte:
        stmt = stmt.where(Produtos.tipo_arte == tipo_arte)

    if nome:
        stmt = stmt.where(Produtos.nome.ilike(f"%{nome}%"))

    if preco_min is not None:
        stmt = stmt.where(Produtos.preco >= preco_min)

    if preco_max is not None:
        stmt = stmt.where(Produtos.preco <= preco_max)

    if ordenar_por == "preco-menor":
        stmt = stmt.order_by(Produtos.preco.asc())
    elif ordenar_por == "preco-maior":
        stmt = stmt.order_by(Produtos.preco.desc())
    elif ordenar_por == "nome":
        stmt = stmt.order_by(Produtos.nome.asc())

    artes = db.execute(stmt).all()

    return [
        {
            "id_produto": produto.id_produto,
            "nome": produto.nome,
            "tipo_arte": produto.tipo_arte,
            "preco": produto.preco,
            "id_usuario": produto.id_usuario,
            "imagem": imagem,
        }
        for produto, imagem in artes
    ]


@arts_router.get("/artist/me", response_model=List[ArteResposta])
async def listar_minhas_artes(
    usuario: Usuarios = Depends(verificar_token),
    db: Session = Depends(pegar_sessao),
):
    stmt = (
        select(Produtos, Imagens_Quadros)
        .join(
            Imagens_Quadros,
            Produtos.id_produto == Imagens_Quadros.id_produto
        )
        .where(Produtos.id_usuario == usuario.id_usuario)
    )
    artes = db.execute(stmt).all()
    return [
        {
            "id_produto": produto.id_produto,
            "nome": produto.nome,
            "tipo_arte": produto.tipo_arte,
            "preco": produto.preco,
            "id_usuario": produto.id_usuario,
            "imagem": imagem,
        }
        for produto, imagem in artes
    ]


@arts_router.get("/artist/{id_usuario}", response_model=List[ArteResposta])
async def listar_artes_do_artista(id_usuario: int, db: Session = Depends(pegar_sessao)):
    stmt = (
        select(Produtos, Imagens_Quadros)
        .join(
            Imagens_Quadros,
            Produtos.id_produto == Imagens_Quadros.id_produto
        )
        .where(Produtos.id_usuario == id_usuario)
    )
    artes = db.execute(stmt).all()
    return [
        {
            "id_produto": produto.id_produto,
            "nome": produto.nome,
            "tipo_arte": produto.tipo_arte,
            "preco": produto.preco,
            "id_usuario": produto.id_usuario,
            "imagem": imagem,
        }
        for produto, imagem in artes
    ]


@arts_router.get("/{id_produto}", response_model=ArteResposta)
async def buscar_arte(id_produto: int, db: Session = Depends(pegar_sessao)):
    arte = buscar_arte_http(id_produto, db)
    imagem_arte = buscar_imagem_arte_http(id_produto, db)
    return montar_dicionario_resposta(arte,imagem_arte)


@arts_router.post("/", response_model=ArteResposta, status_code=status.HTTP_201_CREATED)
async def cadastrar_arte(
    arte_schema: Annotated[
        ArteCadastro,
        Depends(ArteCadastro.as_form),
    ],
    usuario: Usuarios = Depends(verificar_token),
    db: Session = Depends(pegar_sessao),
):
    if usuario.tipo_acesso != "ARTISTA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente artistas podem cadastrar artes",
        )

    public_id = None

    try:
        # 1. Primeiro fazemos o upload no Cloudinary
        url_imagem, public_id = cadastrar_imagem(
            arte_schema.imagem
        )

        # 2. Tudo relacionado ao banco fica dentro
        #    de uma única transação
        with db.begin():

            nova_arte = Produtos(
                nome=arte_schema.nome,
                tipo_arte=arte_schema.tipo_arte,
                preco=arte_schema.preco,
                id_usuario=usuario.id_usuario,
            )

            db.add(nova_arte)

            # flush envia o INSERT para o banco sem
            # finalizar a transação.
            db.flush()

            nova_imagem_arte = Imagens_Quadros(
                id_produto=nova_arte.id_produto,
                imagem=url_imagem,
                imagem_public_id=public_id,
            )

            db.add(nova_imagem_arte)

            db.flush()

        # Aqui o COMMIT já aconteceu.
        db.refresh(nova_arte)
        db.refresh(nova_imagem_arte)

        return {
            "id_produto": nova_arte.id_produto,
            "nome": nova_arte.nome,
            "tipo_arte": nova_arte.tipo_arte,
            "preco": nova_arte.preco,
            "id_usuario": nova_arte.id_usuario,
            "imagem": nova_imagem_arte,
        }

    except Exception as e:

        # Se o banco falhou depois do upload,
        # tentamos compensar excluindo a imagem.
        if public_id:
            try:
                deletar_imagem(public_id)
            except Exception as cloudinary_error:
                print(
                    "ERRO CRÍTICO: não foi possível remover "
                    "a imagem órfã do Cloudinary:",
                    cloudinary_error,
                )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível cadastrar a arte.",
        ) from e


@arts_router.put("/{id_produto}", response_model=ArteResposta)
async def editar_arte(
    id_produto: int,
    arte_schema: Annotated[
        ArteCadastro,
        Depends(ArteCadastro.as_form),
    ],
    usuario: Usuarios = Depends(verificar_token),
    db: Session = Depends(pegar_sessao),
):
    arte = buscar_arte_http(id_produto, db)
    validar_dono_da_arte(arte, usuario)

    arte.nome = arte_schema.nome
    arte.tipo_arte = arte_schema.tipo_arte
    arte.preco = arte_schema.preco

    imagem_arte = buscar_imagem_arte_http(id_produto, db)

    nova_imagem, public_id = atualizar_imagem(arte_schema.imagem,imagem_arte.imagem_public_id)
    imagem_arte.imagem = nova_imagem
    imagem_arte.imagem_public_id = public_id

    db.commit()
    db.refresh(arte)
    db.refresh(imagem_arte)
    return montar_dicionario_resposta(arte,imagem_arte)


@arts_router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_arte(
    id_produto: int,
    usuario: Usuarios = Depends(verificar_token),
    db: Session = Depends(pegar_sessao),
):
    arte = buscar_arte_http(id_produto, db)
    validar_dono_da_arte(arte, usuario)

    imagem_arte = buscar_imagem_arte_http(id_produto, db)

    public_id = imagem_arte.imagem_public_id

    try:

        # -----------------------------------
        # TRANSAÇÃO DO BANCO
        # -----------------------------------

        with db.begin():

            db.delete(imagem_arte)
            db.delete(arte)

        # Se chegamos aqui, o COMMIT aconteceu.
        # O banco agora está consistente.

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível excluir a arte.",
        ) from e

    # -----------------------------------
    # CLOUDINARY
    # -----------------------------------

    try:
        deletar_imagem(public_id)

    except Exception as e:

        # O banco já foi confirmado.
        #
        # NÃO devemos tentar dar rollback no banco,
        # porque o COMMIT já aconteceu.
        #
        # Precisamos registrar o problema para
        # posteriormente tentar excluir a imagem.

        print(
            "ERRO: arte excluída do banco, "
            "mas não foi possível excluir "
            f"a imagem {public_id} do Cloudinary: {e}"
        )

    return None
