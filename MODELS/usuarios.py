from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, Date, CHAR, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC, date
from MODELS import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MODELS.enderecos import Enderecos

class Usuarios(Base):

    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True)

    nome_completo: Mapped[str] = mapped_column(String(150))

    login: Mapped[str] = mapped_column(
        String(50)
        ,unique=True
    )

    senha: Mapped[str] = mapped_column(String(255))

    data_nascimento: Mapped[date] = mapped_column(Date)

    cpf: Mapped[str] = mapped_column(
        CHAR(11)
        ,unique=True
    )

    tipo_acesso: Mapped[str] = mapped_column(
        String(20)
        ,default="CLIENTE"
    )

    enderecos: Mapped[list["Enderecos"]] = relationship(
        "Enderecos",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "length(cpf) = 11"
            ,name="chk_cpf_length"
        )
        ,CheckConstraint(
            "tipo_acesso IN ('CLIENTE','ARTISTA','ADMINISTRADOR')"
            ,name="chk_tipo_acesso_opt"
        ),
    )