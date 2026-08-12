from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CheckConstraint, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from MODELS import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MODELS.pagamentos import Pagamentos
    from MODELS.usuarios import Usuarios


# Guarda os cartões vinculados ao usuário para facilitar pagamentos futuros.
class Cartoes(Base):
    
    __tablename__ = "cartoes"

    id_cartao: Mapped[int] = mapped_column(primary_key=True)

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id_usuario"
            ,name="fk_cartoes_usuario"
            ,ondelete="CASCADE"
        )
    )

    numero_cartao: Mapped[str] = mapped_column(
        String(16)
        ,unique=True
    )

    nome_titular: Mapped[str] = mapped_column(String(100))

    validade: Mapped[str] = mapped_column(
        String(5)
    )

    codigo_seguranca: Mapped[str] = mapped_column(
        String(3)
    )

    tipo: Mapped[str] = mapped_column(
        String(20)
    )

    data_criacao: Mapped[datetime] = mapped_column(
        TIMESTAMP()
        ,server_default=func.current_timestamp()
    )

    pagamentos: Mapped[list["Pagamentos"]] = relationship(
        "Pagamentos"
        ,back_populates="cartao"
    )

    usuario: Mapped["Usuarios"] = relationship(
        "Usuarios"
        ,back_populates="cartoes"
    )

    __table_args__ = (
        CheckConstraint(
            "length(numero_cartao) = 16"
            ,name="chk_numero_cartao_length"
        ),
        CheckConstraint(
            "length(validade) = 5"
            ,name="chk_validade_length"
        ),
        CheckConstraint(
            "length(codigo_seguranca) = 3"
            ,name="chk_cvv_length"
        ),
        CheckConstraint(
            "tipo IN ('CREDITO','DEBITO')"
            ,name="chk_tipo_cartao_opt"
        )
    )
