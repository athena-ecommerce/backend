from sqlalchemy import String, Integer, Boolean, NUMERIC, ForeignKey, DateTime, CheckConstraint, Index, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from MODELS import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MODELS.usuarios import Usuarios
    from MODELS.enderecos import Enderecos


class Pedidos(Base):

    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(primary_key=True)

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id_usuario"
            ,name="fk_pedidos_usuarios"
            ,ondelete="RESTRICT"
        )
    )

    id_endereco: Mapped[int] = mapped_column(
        ForeignKey(
            "enderecos.id_endereco"
            ,name="fk_pedidos_enderecos"
            ,ondelete="RESTRICT"
        )
    )


    valor_total: Mapped[float] = mapped_column(
        NUMERIC(10,2)
        ,default=0.0
    )

    data_pedido: Mapped[datetime] = mapped_column(
        TIMESTAMP()
        ,server_default=func.current_timestamp()
    )

    status: Mapped[str] = mapped_column(
        String(30)
        ,default="PENDENTE"
    )

    tipo_pagamento: Mapped[str] = mapped_column(
        String(30)
    )

    numero_parcela: Mapped[int] = mapped_column(
        Integer
        ,default=1
    )

    usuario: Mapped["Usuarios"] = relationship(
        "Usuarios"
        ,back_populates="pedidos"
    )

    produtos = relationship(
        "Pedidos_Produtos"
        ,back_populates="pedido"
    )

    pagamentos = relationship(
        "Pagamentos"
        ,back_populates="pedido"
    )

    endereco: Mapped["Enderecos"] = relationship(
    "Enderecos"
    ,back_populates="pedidos"
)

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDENTE','EM ANDAMENTO','ENTREGUE','CANCELADO')"
            ,name="chk_status_opt"
        )
        ,CheckConstraint(
            "valor_total >= 0.0"
            ,name="chk_valor_total_positivo"
        ),
        Index(
            "idx_pedidos_data"
            ,"data_pedido"
        ),
        Index(
            "idx_pedidos_endereco"
            ,"id_endereco"
        ),
        Index(
            "idx_pedidos_status"
            ,"status"
        ),
        Index(
            "idx_pedidos_usuario"
            ,"id_usuario"
        ),
    )

