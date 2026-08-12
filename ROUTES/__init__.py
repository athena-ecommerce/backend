from .auth import auth_router
from .produtos import arts_router
from .purchase import purchase_router
from .user import user_router
from .carrinho import cart_router

__all__ = [
    auth_router
    ,arts_router
    ,purchase_router
    ,user_router
    ,cart_router
]