from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from MODELS import Produtos, Pedidos, Enderecos, Usuarios, Pedidos_Produtos
from SCHEMAS import PedidoCompleto, PedidoCompletoResposta
from DEPENDENCIES import pegar_sessao, verificar_token

purchase_route = APIRouter(prefix="/purchase",tags=["Compras"])

def adicionar_pedido(pedido_schema:PedidoCompleto, id_usuario: int, db: Session):
    pedido: Pedidos = Pedidos(
        valor_total=pedido_schema.valor_total
        ,id_usuario=id_usuario
        ,id_endereco=pedido_schema.id_endereco
    )

    db.add(pedido)
    db.commit()
    return db.refresh(pedido)

def adicionar_produtos(ids_produtos: list[int], id_pedido: int, db: Session):
    produtos: list[Pedidos_Produtos] = []
    for id_produto in ids_produtos:
        produtos.append(
            Pedidos_Produtos(
                id_produto=id_produto
                ,id_pedido=id_pedido
            )
        )
    db.add_all(produtos)
    db.commit()
    return db.refresh(produtos)

def listar_pedidos(id_usuario: int, db: Session):
    stmt = select(Pedidos).where(Pedidos.id_usuario == id_usuario).options(
        joinedload(Pedidos.id_endereco)
        ,joinedload(Pedidos.produtos)
        .joinedload(Pedidos_Produtos.produto)
    )
    pedidos: list[PedidoCompletoResposta] = db.scalars(stmt)

    return pedidos




@purchase_route.post("/",response_model=PedidoCompletoResposta)
async def registrar_pedido(pedido_schema: PedidoCompleto, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):

    pedido: Pedidos = adicionar_pedido(pedido_schema=pedido_schema, id_usuario=usuario.id_usuario, db=db)

    produtos: list[Produtos] = adicionar_produtos(ids_produtos=pedido_schema.ids_produto,id_pedido=pedido.id_pedido, db=db)


@purchase_route.post("/payment",)
async def realizar_pagamento():
    pass


@purchase_route.get("/",response_model=list[PedidoCompletoResposta])
async def listar_pedidos(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    return listar_pedidos(usuario.id_usuario,db)
