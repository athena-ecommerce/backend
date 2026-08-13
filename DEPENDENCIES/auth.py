from MODELS import Usuarios
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy import select
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from CORE import SECRET_KEY, ALGORITHM, oauth2_schema
from DEPENDENCIES import pegar_sessao

def verificar_token_oauth(token: str = Depends(oauth2_schema), db:Session = Depends(pegar_sessao)):
    # Decodifica o token OAuth2 e transforma o subject em um usuário do banco.
    try:
        dic_info = jwt.decode(token,SECRET_KEY,ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado! Verfique a validade do token.")
    #Verificar se o token é válido
    #Extrair o id_usuario
    stmt = select(Usuarios).where(Usuarios.id_usuario == id_usuario)
    usuario = db.scalar(stmt)
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido!")
    return usuario

def verificar_token(token: str = Depends(oauth2_schema), db: Session = Depends(pegar_sessao)):
    # A dependência bloqueia rotas protegidas antes que sua lógica principal seja executada.
    try:
        dic_info = jwt.decode(token,SECRET_KEY,ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado! Verfique a validade do token.")
    #Verificar se o token é válido
    #Extrair o id_usuario
    stmt = select(Usuarios).where(Usuarios.id_usuario == id_usuario)
    usuario = db.scalar(stmt)
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido!")
    return usuario
