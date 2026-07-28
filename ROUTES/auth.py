from fastapi import APIRouter, Depends, HTTPException
from SCHEMAS import UsuarioCadastro, UsuarioCadastroResposta
from MODELS import Usuarios
from DEPENDENCIES import pegar_sessao
from sqlalchemy.orm import Session
from sqlalchemy import select
from CORE import bcrypt_context

auth_router = APIRouter(prefix="/auth",tags=["Autenticação"])

def usuario_existe(usuario: Usuarios, db: Session):
    usuario = db.scalar(select(Usuarios).where(Usuarios.login == usuario.login))
    if usuario:
        return True
    else:
        return False

def cadastrar_usuario(usuario: Usuarios, db: Session):
    print(len(usuario.senha.encode("utf-8")))
    senha_criptografada = bcrypt_context.hash(usuario.senha)
    usuario.senha = senha_criptografada

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@auth_router.post("/cadastrar", response_model=UsuarioCadastroResposta)
async def cadastrar(usuario_schema: UsuarioCadastro, db: Session = Depends(pegar_sessao)):
    novo_usuario = Usuarios(
        nome_completo=usuario_schema.nome_completo, 
        login=usuario_schema.login, 
        senha=usuario_schema.senha, 
        data_nascimento=usuario_schema.data_nascimento, 
        cpf=usuario_schema.cpf,
        tipo_acesso=usuario_schema.tipo_acesso
    )
    if usuario_existe(novo_usuario,db):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    else:
        return cadastrar_usuario(novo_usuario,db)