from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Pedidos(Base):

    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(primary_key=True)

    valor_total: Mapped[float] = mapped_column(
        Float(10,2)
        ,default=0.0
    )

    data_pedido: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
        ,default=lambda: datetime.now(UTC)
    )

    status: Mapped[str] = mapped_column(
        String(30)
        ,default="PENDENTE"
    )

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    id_endereco: Mapped[int] = mapped_column(ForeignKey("enderecos.id"))

