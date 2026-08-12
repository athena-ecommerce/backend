from sqlalchemy.orm import DeclarativeBase

# Todas as entidades herdam desta base para compartilhar o mapeamento do SQLAlchemy.
class Base(DeclarativeBase):
    pass
