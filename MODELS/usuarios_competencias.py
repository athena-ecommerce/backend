from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Usuarios_Competencias(Base):
    # Tabela associativa que liga usuários às competências cadastradas.

    __tablename__ = "usuarios_competencias"

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(
            "usuarios.id_usuario"
            ,name="fk_usuarios_comp_usuarios"
            ,ondelete="CASCADE"
        )
        ,primary_key=True
    )

    id_competencia: Mapped[int] = mapped_column(
        ForeignKey(
            "competencias.id_competencia"
            ,name="fk_usuarios_comp_competencia"
            ,ondelete="CASCADE"
        )
        ,primary_key=True
    )

    __table_args__ = (
        Index(
            "idx_usuarios_comp_competencia"
            ,"id_competencia"
        ),
    )

