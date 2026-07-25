from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

SessionLocal = sessionmaker(bind=engine)