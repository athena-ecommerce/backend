from .auth import auth_router
from .produtos import arts_router
from .purchase import purchase_route

__all__ = [
    auth_router
    ,arts_router
    ,purchase_route
]