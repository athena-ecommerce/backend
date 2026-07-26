from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from DEPENDENCIES.session import pegar_sessao
from MODELS import Produtos

arts_router = APIRouter(prefix="/arts", tags=["Arts"])

@arts_router.get("/")
def listar_artes(db: Session = Depends(pegar_sessao)):
    stmt = select(Produtos)

    artes = db.scalars(stmt).all()

    return artes