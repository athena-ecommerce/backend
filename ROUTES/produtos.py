from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from DEPENDENCIES import pegar_sessao, usuario_logado
from MODELS import Produtos, Usuarios
from SCHEMAS import ArteAtualizar, ArteCadastro, ArteResposta

arts_router = APIRouter(prefix="/arts", tags=["Artes"])


def buscar_arte_http(id_produto: int, db: Session) -> Produtos:
    arte = db.get(Produtos, id_produto)

    if not arte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arte não encontrada",
        )

    return arte


def validar_dono_da_arte(arte: Produtos, usuario: Usuarios):
    if arte.id_usuario != usuario.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Essa arte não pertence a você",
        )


@arts_router.get("/", response_model=List[ArteResposta])
async def listar_artes(db: Session = Depends(pegar_sessao)):
    stmt = select(Produtos)
    artes = db.scalars(stmt).all()
    return artes


@arts_router.get("/artist/me/", response_model=List[ArteResposta])
async def listar_minhas_artes(
    usuario: Usuarios = Depends(usuario_logado),
    db: Session = Depends(pegar_sessao),
):
    stmt = select(Produtos).where(Produtos.id_usuario == usuario.id_usuario)
    artes = db.scalars(stmt).all()
    return artes


@arts_router.get("/artist/{id_usuario}", response_model=List[ArteResposta])
async def listar_artes_do_artista(id_usuario: int, db: Session = Depends(pegar_sessao)):
    stmt = select(Produtos).where(Produtos.id_usuario == id_usuario)
    artes = db.scalars(stmt).all()
    return artes


@arts_router.get("/{id_produto}", response_model=ArteResposta)
async def buscar_arte(id_produto: int, db: Session = Depends(pegar_sessao)):
    return buscar_arte_http(id_produto, db)


@arts_router.post("/", response_model=ArteResposta, status_code=status.HTTP_201_CREATED)
async def cadastrar_arte(
    arte_schema: ArteCadastro,
    usuario: Usuarios = Depends(usuario_logado),
    db: Session = Depends(pegar_sessao),
):
    if usuario.tipo_acesso != "ARTISTA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente artistas podem cadastrar artes",
        )

    nova_arte = Produtos(
        nome=arte_schema.nome,
        tipo_arte=arte_schema.tipo_arte,
        preco=arte_schema.preco,
        id_usuario=usuario.id_usuario,
    )

    db.add(nova_arte)
    db.commit()
    db.refresh(nova_arte)
    return nova_arte


@arts_router.put("/{id_produto}", response_model=ArteResposta)
async def editar_arte(
    id_produto: int,
    arte_schema: ArteAtualizar,
    usuario: Usuarios = Depends(usuario_logado),
    db: Session = Depends(pegar_sessao),
):
    arte = buscar_arte_http(id_produto, db)
    validar_dono_da_arte(arte, usuario)

    arte.nome = arte_schema.nome
    arte.tipo_arte = arte_schema.tipo_arte
    arte.preco = arte_schema.preco

    db.commit()
    db.refresh(arte)
    return arte


@arts_router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_arte(
    id_produto: int,
    usuario: Usuarios = Depends(usuario_logado),
    db: Session = Depends(pegar_sessao),
):
    arte = buscar_arte_http(id_produto, db)
    validar_dono_da_arte(arte, usuario)

    db.delete(arte)
    db.commit()
