from sqlalchemy import String, Integer, Boolean, NUMERIC, ForeignKey, DateTime, CheckConstraint, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from MODELS import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MODELS.pedidos_produtos import Pedidos_Produtos

# Cada obra pertence a um usuário e pode ser referenciada em pedidos e no carrinho.
class Produtos(Base):
    
    __tablename__ = "produtos"

    id_produto: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(String(150))

    tipo_arte: Mapped[str] = mapped_column(String(100))

    preco: Mapped[float] = mapped_column(NUMERIC(10,2))

    descricao: Mapped[str] = mapped_column(Text)

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id_usuario"
            ,name="fk_produtos_usuarios"
            ,ondelete="RESTRICT"
        )
    )
    
    pedidos_produtos: Mapped[list["Pedidos_Produtos"]] = relationship(
    "Pedidos_Produtos"
    ,back_populates="produto"
)

    __table_args__ = (
        CheckConstraint(
            "preco >= 0.0"
            ,name="chk_preco_positivo"
        ),
        Index(
            "idx_produtos_nome"
            ,"nome"
        ),
        Index(
            "idx_produtos_usuario"
            ,"id_usuario"
        ),
    )
