from sqlalchemy import String, Integer, Boolean, NUMERIC, ForeignKey, DateTime, CheckConstraint, Index, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Pedidos(Base):

    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(primary_key=True)

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

