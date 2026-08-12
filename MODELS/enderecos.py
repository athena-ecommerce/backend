from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CHAR, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from MODELS import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MODELS.usuarios import Usuarios
    from MODELS.pedidos import Pedidos

class Enderecos(Base):

    __tablename__ = "enderecos"

    id_endereco: Mapped[int] = mapped_column(primary_key=True)

    rua: Mapped[str] = mapped_column(String(150))

    bairro: Mapped[str] = mapped_column(String(100))

    estado: Mapped[str] = mapped_column(CHAR(2))

    numero: Mapped[str] = mapped_column(String(20))

    complemento: Mapped[str | None] = mapped_column(
        String(100)
        ,nullable=True
    )

    cep: Mapped[str] = mapped_column(CHAR(8))

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id_usuario"
            ,name="fk_enderecos_usuarios"
            ,ondelete="CASCADE"
        )
    )

    usuario: Mapped["Usuarios"] = relationship(
        "Usuarios"
        ,back_populates="enderecos"
    )

    pedidos: Mapped[list["Pedidos"]] = relationship(
    "Pedidos"
    ,back_populates="endereco"
)

    __table_args__ = (
        CheckConstraint(
            "length(cep) = 8"
            ,name="chk_cep_length"
        ),
        Index(
            "idx_enderecos_usuario"
            ,"id_usuario"
        ),
    )