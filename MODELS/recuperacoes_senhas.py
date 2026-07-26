from sqlalchemy import String, Integer, Boolean, NUMERIC, ForeignKey, DateTime, CheckConstraint, Index, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Recuperacoes_Senhas(Base):

    __tablename__ = "recuperacoes_senhas"

    id_recuperacao_senha: Mapped[int] = mapped_column(primary_key=True)

    login: Mapped[str] = mapped_column(String(150))

    codigo: Mapped[str] = mapped_column(String(250))

    tempo_expiracao: Mapped[datetime] = mapped_column(TIMESTAMP())

    usado: Mapped[bool] = mapped_column(Boolean)

    data_criacao: Mapped[datetime] = mapped_column(
        TIMESTAMP()
        ,server_default=func.current_timestamp()
    )