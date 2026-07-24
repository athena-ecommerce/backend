from sqlalchemy.orm import Session, sessionmaker
from DEPENDENCIES import database

def pegar_sessao():
    try:
        db = database.gerar_conexao()

        Session = sessionmaker(bind=db)
        session = Session()

        yield session
    finally:
        session.close_all()
    