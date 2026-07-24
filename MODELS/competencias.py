from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from MODELS import Base

class Competencias(Base):

    __tablename__ = "competencias"

    id_competencia: Mapped[int] = mapped_column(primary_key=True)

    nome_competencia: Mapped[str] = mapped_column(String(100))

    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
        ,default=lambda: datetime.now(UTC)
    )