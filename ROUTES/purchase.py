from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from MODELS import Pedidos, Usuarios, Pedidos_Produtos, Cartoes, Pagamentos, Enderecos, Produtos
from DEPENDENCIES import pegar_sessao, verificar_token
from SCHEMAS.card_schema import CartaoCadastro, CartaoResponse
from SCHEMAS.pedido_produto_schema import PedidosProdutosSchema
from SCHEMAS.pedido_schema import PedidoCompleto, PedidoCompletoResposta, PedidoResponse
from SCHEMAS.purchase_schema import PagamentoSchema, PagamentoResponse, PagamentoCartaoCompleto, PagamentoCartaoCompletoResposta
from uuid import uuid4
import secrets

purchase_router = APIRouter(prefix="/purchase",tags=["Compras"])

# Pedidos
# Lista somente os pedidos pertencentes ao comprador autenticado.
@purchase_router.get("/",response_model=list[PedidoResponse])
async def listar_pedidos(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    pedidos = db.query(Pedidos).filter(Pedidos.id_usuario == usuario.id_usuario).all()
    return pedidos


# Cria o pedido principal e registra nele cada produto escolhido no checkout.
@purchase_router.post("/", response_model=PedidoResponse)
async def criar_pedido(pedido_schema: PedidoCompleto, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    endereco = db.query(Enderecos).filter(
        Enderecos.id_endereco == pedido_schema.id_endereco,
        Enderecos.id_usuario == usuario.id_usuario,
    ).first()
    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço de entrega não encontrado.")

    subtotal = 0.0
    for item in pedido_schema.produtos:
        produto = db.get(Produtos, item.id_produto)
        if not produto:
            raise HTTPException(status_code=404, detail=f"Obra {item.id_produto} não encontrada.")
        subtotal += float(produto.preco) * item.quantidade
    frete = 29.9 if endereco.estado == "SP" else 49.9
    if abs((subtotal + frete) - pedido_schema.valor_total) > 0.01:
        raise HTTPException(status_code=400, detail="O total do pedido não corresponde às obras e ao frete.")

    novo_pedido = Pedidos(
        id_usuario=usuario.id_usuario,
        id_endereco=pedido_schema.id_endereco,
        valor_total=pedido_schema.valor_total,
        tipo_pagamento="PENDENTE",
        numero_parcela=1,
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
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao criar o pedido.")

    db.refresh(novo_pedido)
    return novo_pedido



# Cartões
# Salva um cartão para que o usuário possa reutilizá-lo em pagamentos futuros.
@purchase_router.post("/card", response_model=CartaoResponse)
async def adicionar_cartao(cartao_schema: CartaoCadastro, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    cartao_novo = Cartoes(
        id_usuario=usuario.id_usuario
        ,numero_cartao=f"{secrets.randbelow(10**12):012d}" + cartao_schema.numero_cartao[-4:]
        ,nome_titular=cartao_schema.nome_titular
        ,validade=cartao_schema.validade
        ,codigo_seguranca="***"
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
    return CartaoResponse(
        id_cartao=cartao_novo.id_cartao,
        nome_titular=cartao_novo.nome_titular,
        validade=cartao_novo.validade,
        tipo=cartao_novo.tipo,
        final_cartao=cartao_novo.numero_cartao[-4:],
    )


# Lista os cartões da conta sem retornar os dados sensíveis completos.
@purchase_router.get("/card", response_model=list[CartaoResponse])
async def listar_cartoes(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    cartoes = db.query(Cartoes).filter(Cartoes.id_usuario == usuario.id_usuario).all()
    return [
        CartaoResponse(
            id_cartao=cartao.id_cartao,
            nome_titular=cartao.nome_titular,
            validade=cartao.validade,
            tipo=cartao.tipo,
            final_cartao=cartao.numero_cartao[-4:],
        )
        for cartao in cartoes
    ]


# Exclui um cartão apenas quando ele pertence ao usuário autenticado.
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
# Gera uma chave única que identifica a cobrança PIX atual.
@purchase_router.get("/pix-key")
async def criar_chave_pix():
    chave_pix = str(uuid4())
    
    return {"chave_pix": chave_pix}


# Registra o pagamento usando o cartão ou a chave PIX informada no payload.
@purchase_router.post("/payment", response_model=PagamentoResponse)
async def realizar_pagamento(pagamento_schema: PagamentoSchema, usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    pedido = db.query(Pedidos).filter(Pedidos.id_pedido == pagamento_schema.id_pedido, Pedidos.id_usuario == usuario.id_usuario).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if pagamento_schema.id_cartao:
        cartao = db.query(Cartoes).filter(Cartoes.id_cartao == pagamento_schema.id_cartao, Cartoes.id_usuario == usuario.id_usuario).first()
        if not cartao:
            raise HTTPException(status_code=404, detail="Cartão não encontrado.")
    novo_pagamento = Pagamentos(
        id_pedido=pagamento_schema.id_pedido,
        id_cartao=pagamento_schema.id_cartao,
        chave_pix=pagamento_schema.chave_pix,
        valor=pagamento_schema.valor,
        numero_parcela=pagamento_schema.numero_parcelas
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


# Consulta o histórico de pagamentos da conta atual.
@purchase_router.get("/payment", response_model=list[PagamentoResponse])
async def listar_pagamentos(usuario: Usuarios = Depends(verificar_token), db: Session = Depends(pegar_sessao)):
    return (
        db.query(Pagamentos)
        .join(Pedidos, Pedidos.id_pedido == Pagamentos.id_pedido)
        .filter(Pedidos.id_usuario == usuario.id_usuario)
        .all()
    )


# Executa o fluxo completo de cartão novo: pedido, cartão e pagamento em uma operação.
@purchase_router.post("/card-payment", response_model=PagamentoCartaoCompletoResposta)
async def pagar_com_cartao(
    dados: PagamentoCartaoCompleto,
    usuario: Usuarios = Depends(verificar_token),
    db: Session = Depends(pegar_sessao),
):
    endereco = db.query(Enderecos).filter(
        Enderecos.id_endereco == dados.id_endereco,
        Enderecos.id_usuario == usuario.id_usuario,
    ).first()
    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço de entrega não encontrado.")
    if dados.tipo == "DEBITO" and dados.numero_parcelas != 1:
        raise HTTPException(status_code=400, detail="Pagamento no débito deve ser feito em uma parcela.")

    subtotal = 0.0
    produtos_validos = []
    for item in dados.produtos:
        produto = db.get(Produtos, item.id_produto)
        if not produto:
            raise HTTPException(status_code=404, detail=f"Obra {item.id_produto} não encontrada.")
        subtotal += float(produto.preco) * item.quantidade
        produtos_validos.append(item)

    frete = 29.9 if endereco.estado == "SP" else 49.9
    if abs((subtotal + frete) - dados.valor_total) > 0.01:
        raise HTTPException(status_code=400, detail="O total do pedido mudou. Volte ao carrinho e tente novamente.")

    pedido = Pedidos(
        id_usuario=usuario.id_usuario,
        id_endereco=dados.id_endereco,
        valor_total=dados.valor_total,
        tipo_pagamento=dados.tipo,
        numero_parcela=dados.numero_parcelas,
    )
    cartao = Cartoes(
        id_usuario=usuario.id_usuario,
        numero_cartao=f"{secrets.randbelow(10**12):012d}" + dados.numero_cartao[-4:],
        nome_titular=dados.nome_titular,
        validade=dados.validade,
        codigo_seguranca="***",
        tipo=dados.tipo,
    )

    try:
        db.add(pedido)
        db.flush()
        for item in produtos_validos:
            db.add(Pedidos_Produtos(id_produto=item.id_produto, id_pedido=pedido.id_pedido, quantidade=item.quantidade))
        db.add(cartao)
        db.flush()
        pagamento = Pagamentos(
            id_pedido=pedido.id_pedido,
            id_cartao=cartao.id_cartao,
            chave_pix=None,
            valor=dados.valor_total,
            numero_parcela=dados.numero_parcelas,
        )
        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível concluir o pagamento com os dados informados.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao concluir o pagamento.")

    return PagamentoCartaoCompletoResposta(
        id_pedido=pedido.id_pedido,
        id_pagamento=pagamento.id_pagamento,
        status="APROVADO",
    )
