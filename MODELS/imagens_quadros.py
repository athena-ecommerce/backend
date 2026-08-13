from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, CHAR, CheckConstraint, Index, LargeBinary, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from MODELS import Base
from typing import TYPE_CHECKING

class Imagens_Quadros(Base):
    # Armazena a URL e os metadados da imagem hospedada no Cloudinary.

    __tablename__ = "imagens_quadros"

    id_imagem_quadro: Mapped[int] = mapped_column(primary_key=True)

    imagem: Mapped[str] = mapped_column(Text)

    imagem_public_id: Mapped[str] = mapped_column(String(100))

    descricao_foto: Mapped[str] = mapped_column(Text)

    dimensoes: Mapped[str] = mapped_column(String(100))

    id_produto: Mapped[int] = mapped_column(
        ForeignKey(
            "produtos.id_produto"
            ,name="fk_imagens_quadros_produtos"
            ,ondelete="CASCADE"
        )
    )
