from sqlalchemy import create_engine, Engine
from dotenv import load_dotenv
import os

load_dotenv()

def gerar_conexao() -> Engine:
    return create_engine(
        os.getenv("DATABASE_URL")
    )