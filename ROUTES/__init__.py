from .auth import auth_router
from .produtos import arts_router
from .carrinho import cart_router

__all__ = [
    auth_router
    ,arts_router
    ,cart_router
]