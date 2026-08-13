from sqlalchemy.orm import Session, sessionmaker
from DEPENDENCIES import SessionLocal

def pegar_sessao() -> Session:
    # Abre uma sessão por requisição e garante o fechamento mesmo quando ocorre uma exceção.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()
