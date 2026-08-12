from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from MODELS import Pedidos, Usuarios, Pedidos_Produtos, Cartoes, Pagamentos
from DEPENDENCIES import pegar_sessao, verificar_token
from SCHEMAS.card_schema import CartaoCadastro, CartaoResponse
from SCHEMAS.pedido_produto_schema import PedidosProdutosSchema
from SCHEMAS.pedido_schema import PedidoCompleto, PedidoResponse, ListaPedidosResponse
from SCHEMAS.purchase_schema import PagamentoSchema, PagamentoResponse
from uuid import uuid4

purchase_router = APIRouter(prefix="/purchase",tags=["Compras"])

# Pedidos
@purchase_router.get("/orders",response_model=ListaPedidosResponse)
async def listar_pedidos(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    pedidos = db.query(Pedidos).filter(Pedidos.id_usuario == usuario.id_usuario).all()
    return {"pedidos": pedidos}


@purchase_router.post("/orders", response_model=PedidoResponse)
async def criar_pedido(pedido_schema: PedidoCompleto, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    novo_pedido = Pedidos(
        id_usuario=usuario.id_usuario,
        id_endereco=pedido_schema.id_endereco,
        valor_total=pedido_schema.valor_total
    )

    db.add(novo_pedido)
    db.flush()

    for produto in pedido_schema.produtos:
        pedido_produto = Pedidos_Produtos(
            id_produto=produto.id_produto,
            id_pedido=novo_pedido.id_pedido,
            quantidade=produto.quantidade
        )
        db.add(pedido_produto)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível criar o pedido.")
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao criar o pedido.")

    db.refresh(novo_pedido)
    return novo_pedido



# Cartões
@purchase_router.post("/card", response_model=CartaoResponse)
async def adicionar_cartao(cartao_schema: CartaoCadastro, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    cartao_novo = Cartoes(
        id_usuario=usuario.id_usuario
        ,numero_cartao=cartao_schema.numero_cartao
        ,nome_titular=cartao_schema.nome_titular
        ,validade=cartao_schema.validade
        ,codigo_seguranca=cartao_schema.codigo_seguranca
        ,tipo=cartao_schema.tipo
    )
    
    db.add(cartao_novo)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível adicionar o cartão.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao adicionar o cartão.")

    db.refresh(cartao_novo)
    return cartao_novo


@purchase_router.get("/card", response_model=list[CartaoResponse])
async def listar_cartoes(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    cartoes = db.query(Cartoes).filter(Cartoes.id_usuario == usuario.id_usuario).all()
    return cartoes


@purchase_router.delete("/card/{id_cartao}", status_code=204)
async def deletar_cartao(id_cartao: int, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    cartao = db.query(Cartoes).filter(Cartoes.id_cartao == id_cartao, Cartoes.id_usuario == usuario.id_usuario).first()
    
    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")

    try:
        db.delete(cartao)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao deletar o cartão.")



# Pagamentos
@purchase_router.get("/pix-key")
async def criar_chave_pix():
    chave_pix = str(uuid4())
    
    return {"chave_pix": chave_pix}


@purchase_router.post("/payment", response_model=PagamentoResponse)
async def realizar_pagamento(pagamento_schema: PagamentoSchema, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    novo_pagamento = Pagamentos(
        id_usuario=usuario.id_usuario,
        id_cartao=pagamento_schema.id_cartao,
        chave_pix=pagamento_schema.chave_pix,
        valor=pagamento_schema.valor,
        numero_parcelas=pagamento_schema.numero_parcelas
    )
    
    db.add(novo_pagamento)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível realizar o pagamento.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao realizar o pagamento.")
    
    db.refresh(novo_pagamento)
    return novo_pagamento


@purchase_router.get("/payment", response_model=list[PagamentoResponse])
async def listar_pagamentos(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    pagamentos = db.query(Pagamentos).filter(Pagamentos.id_usuario == usuario.id_usuario).all()
    return {"pagamentos": pagamentos}