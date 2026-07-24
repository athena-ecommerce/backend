from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CHAR
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Enderecos(Base):

    __tablename__ = "enderecos"

    id_endereco: Mapped[int] = mapped_column(primary_key=True)

    rua: Mapped[str] = mapped_column(String(150))

    bairro: Mapped[str] = mapped_column(String(100))

    estado: Mapped[str] = mapped_column(CHAR(2))

    numero: Mapped[str] = mapped_column(String(20))

    complemento: Mapped[str] = mapped_column(String(100))

    cep: Mapped[str] = mapped_column(CHAR(8))

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))