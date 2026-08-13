from sqlalchemy import TIMESTAMP, CheckConstraint, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC

from MODELS import Base


class Pagamentos(Base):
    # Registra uma transação ligada ao pedido, usando cartão ou PIX como método.
    __tablename__ = "pagamentos"

    id_pagamento: Mapped[int] = mapped_column(primary_key=True)

    id_pedido: Mapped[int] = mapped_column(
        ForeignKey(
            "pedidos.id_pedido"
            ,name="fk_pagamentos_pedido"
            ,ondelete="CASCADE"
        )
    )

    id_cartao: Mapped[int | None] = mapped_column(
        ForeignKey(
            "cartoes.id_cartao"
            ,name="fk_pagamentos_cartao"
            ,ondelete="CASCADE"
        )
        ,nullable=True
    )

    chave_pix: Mapped[str | None] = mapped_column(
        String(36)
        ,nullable=True
    )

    valor: Mapped[float] = mapped_column(Numeric(10, 2))

    numero_parcela: Mapped[int] = mapped_column(
        Integer
    )

    data_pagamento: Mapped[datetime] = mapped_column(
        TIMESTAMP()
        ,server_default=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint(
            "numero_parcela > 0"
            ,name="chk_numero_parcela_positivo"
        ),
        CheckConstraint(
            "valor >= 0"
            ,name="chk_valor_positivo"
        ),
        CheckConstraint(
            "(id_cartao IS NOT NULL AND chave_pix IS NULL) OR "
            "(id_cartao IS NULL AND chave_pix IS NOT NULL)"
            ,name="chk_pagamento_um_metodo"
        ),
    )

    pedido = relationship(
        "Pedidos",
        back_populates="pagamentos",
    )

    cartao = relationship(
        "Cartoes",
        back_populates="pagamentos",
    )
