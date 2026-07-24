from sqlalchemy import create_engine, Engine

def gerar_conexao() -> Engine:
    return create_engine()