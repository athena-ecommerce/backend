from .database import Base
from .competencias import Competencias
from .enderecos import Enderecos
from .pedidos import Pedidos
from .pedidos_produtos import Pedidos_Produtos
from .produtos import Produtos
from .telefones import Telefones
from .usuarios import Usuarios
from .cartoes import Cartoes
from .pagamentos import Pagamentos
from .usuarios_competencias import Usuarios_Competencias
from .recuperacoes_senhas import Recuperacoes_Senhas
from .imagens_quadros import Imagens_Quadros

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
    ,Recuperacoes_Senhas
    ,Imagens_Quadros
    ,Cartoes
    ,Pagamentos
]