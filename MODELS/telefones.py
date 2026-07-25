from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CHAR, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Telefones(Base):

    __tablename__ = "telefones"

    id_telefone: Mapped[int] = mapped_column(primary_key=True)

    ddd: Mapped[str] = mapped_column(CHAR(2))

    numero: Mapped[str] = mapped_column(String(10))

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id_usuario"
            ,name="fk_telefones_usuarios"
            ,ondelete="CASCADE"
        )
    )

    __table_args__ = (
        CheckConstraint(
            "length(ddd) = 2"
            ,name="chk_ddd_length"
        ),
        Index(
            "idx_telefones_usuario"
            ,"id_usuario"
        ),
    )