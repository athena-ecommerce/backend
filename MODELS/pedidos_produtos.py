from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from MODELS import Base

class Pedidos_Produtos(Base):

    __tablename__ = "pedidos_produtos"

    id_produto: Mapped[int] = mapped_column(
        ForeignKey(
            "produtos.id_produto"
            ,name="fk_pedidos_prod_produto"
            ,ondelete="RESTRICT"
        )
        ,primary_key=True
    )

    id_pedido: Mapped[int] = mapped_column(
        ForeignKey(
            "pedidos.id_pedido"
            ,name="fk_pedidos_prod_pedido"
            ,ondelete="CASCADE"
        )
        ,primary_key=True
    )

    pedido = relationship(
        "Pedidos"
        ,back_populates="produtos"
    )

    produto = relationship("Produtos")

    __table_args__ = (
        Index(
            "idx_pedidos_prod_pedido"
            ,"id_pedido"
        ),
    )
