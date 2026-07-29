import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from DEPENDENCIES import pegar_sessao, verificar_token_oauth, pegar_redis
from MODELS import Produtos, Usuarios
from SCHEMAS import CarrinhoResposta, ItemCarrinhoAdicionar, ItemCarrinhoResposta

cart_router = APIRouter(prefix="/cart", tags=["Carrinho"])

# O carrinho de cada usuário fica em um HASH do Redis:
# chave -> "carrinho:{id_usuario}"
# campo -> id_produto (str)
# valor -> quantidade (str)
CARRINHO_TTL_SEGUNDOS = 60 * 60 * 24 * 7  # 7 dias sem mexer no carrinho, ele expira


def chave_carrinho(id_usuario: int) -> str:
    return f"carrinho:{id_usuario}"


def montar_resposta_carrinho(
    usuario: Usuarios,
    db: Session,
    redis_cliente: redis.Redis,
) -> CarrinhoResposta:
    chave = chave_carrinho(usuario.id_usuario)
    itens_redis = redis_cliente.hgetall(chave)

    itens_resposta = []
    total = 0.0

    for id_produto_str, quantidade_str in itens_redis.items():
        produto = db.get(Produtos, int(id_produto_str))

        if not produto:
            # a arte pode ter sido deletada depois de ter sido colocada no carrinho
            continue

        quantidade = int(quantidade_str)
        subtotal = float(produto.preco) * quantidade
        total += subtotal

        itens_resposta.append(
            ItemCarrinhoResposta(
                id_produto=produto.id_produto,
                nome=produto.nome,
                preco=float(produto.preco),
                quantidade=quantidade,
                subtotal=subtotal,
            )
        )

    return CarrinhoResposta(itens=itens_resposta, total=total)


@cart_router.get("/", response_model=CarrinhoResposta)
async def ver_carrinho(
    usuario: Usuarios = Depends(verificar_token_oauth),
    db: Session = Depends(pegar_sessao),
    redis_cliente: redis.Redis = Depends(pegar_redis),
):
    return montar_resposta_carrinho(usuario, db, redis_cliente)


@cart_router.post("/items", response_model=CarrinhoResposta, status_code=status.HTTP_201_CREATED)
async def adicionar_item(
    item: ItemCarrinhoAdicionar,
    usuario: Usuarios = Depends(verificar_token_oauth),
    db: Session = Depends(pegar_sessao),
    redis_cliente: redis.Redis = Depends(pegar_redis),
):
    produto = db.get(Produtos, item.id_produto)

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arte não encontrada",
        )

    chave = chave_carrinho(usuario.id_usuario)

    quantidade_atual = redis_cliente.hget(chave, str(item.id_produto))
    nova_quantidade = int(quantidade_atual or 0) + item.quantidade

    redis_cliente.hset(chave, str(item.id_produto), nova_quantidade)
    redis_cliente.expire(chave, CARRINHO_TTL_SEGUNDOS)

    return montar_resposta_carrinho(usuario, db, redis_cliente)


@cart_router.delete("/items/{art_id}", response_model=CarrinhoResposta)
async def remover_item(
    art_id: int,
    usuario: Usuarios = Depends(verificar_token_oauth),
    db: Session = Depends(pegar_sessao),
    redis_cliente: redis.Redis = Depends(pegar_redis),
):
    chave = chave_carrinho(usuario.id_usuario)
    redis_cliente.hdel(chave, str(art_id))

    return montar_resposta_carrinho(usuario, db, redis_cliente)


@cart_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def limpar_carrinho(
    usuario: Usuarios = Depends(verificar_token_oauth),
    redis_cliente: redis.Redis = Depends(pegar_redis),
):
    chave = chave_carrinho(usuario.id_usuario)
    redis_cliente.delete(chave)
