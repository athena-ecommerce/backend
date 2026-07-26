from .database import Base
from .competencias import Competencias
from .enderecos import Enderecos
from .pedidos import Pedidos
from .pedidos_produtos import Pedidos_Produtos
from .produtos import Produtos
from .telefones import Telefones
from .usuarios import Usuarios
from .usuarios_competencias import Usuarios_Competencias

__all__ = [
    Base
    ,Competencias
    ,Enderecos
    ,Pedidos
    ,Pedidos_Produtos
    ,Produtos
    ,Telefones
    ,Usuarios
    ,Usuarios_Competencias
]