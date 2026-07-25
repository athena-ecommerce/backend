from sqlalchemy.orm import Session, sessionmaker
from DEPENDENCIES import SessionLocal

def pegar_sessao() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()