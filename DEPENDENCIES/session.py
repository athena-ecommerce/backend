from sqlalchemy.orm import Session, sessionmaker
from DEPENDENCIES import SessionLocal

# Cada requisição recebe uma sessão própria, encerrada ao final da dependência.
def pegar_sessao() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()
