from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from SCHEMAS import UsuarioCadastro, UsuarioCadastroResposta, UsuarioLoginResposta, UsuarioLogin, RecuperarSenha, RecuperarSenhaCodigo, RecuperarSenhaNovaSenha
from MODELS import Usuarios, Recuperacoes_Senhas
from DEPENDENCIES import pegar_sessao, verificar_token_oauth, verificar_token
from sqlalchemy.orm import Session
from sqlalchemy import select
from CORE import bcrypt_context, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from dotenv import load_dotenv
import os
import secrets

conf = ConnectionConfig(
    MAIL_USERNAME=str(os.getenv("ATHENA_EMAIL")),
    MAIL_PASSWORD=str(os.getenv("ATHENA_PASSWORD")),
    MAIL_FROM=str(os.getenv("ATHENA_EMAIL")),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

auth_router = APIRouter(prefix="/auth",tags=["Autenticação"])

def usuario_existe(usuario: Usuarios, db: Session):
    usuario = db.scalar(select(Usuarios).where(Usuarios.login == usuario.login))
    if usuario:
        return True
    else:
        return False

def cadastrar_usuario(usuario: Usuarios, db: Session):
    senha_criptografada = bcrypt_context.hash(usuario.senha)
    usuario.senha = senha_criptografada

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def validar_login(login:str, senha:str, db:Session):
    stmt = select(Usuarios).where(Usuarios.login == login)
    usuario = db.scalar(stmt)

    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario

def criar_token(id_usuario: str, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),tipo="access"):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_inf = {
        "sub": str(id_usuario),
        "exp":data_expiracao,
        "type":tipo
    }

    try:
        jwt_codificado = jwt.encode(dic_inf,SECRET_KEY,ALGORITHM)
    except JWTError as erro:
        return False
    return jwt_codificado


@auth_router.post("/signup", response_model=UsuarioCadastroResposta)
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

@auth_router.post("/login", response_model=UsuarioLoginResposta)
async def login(login_schema: UsuarioLogin, db: Session = Depends(pegar_sessao)):
    usuario = validar_login(login_schema.login,login_schema.senha, db)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado!")

    access_token = criar_token(usuario.id_usuario)
    if not access_token:
        raise HTTPException(status_code=400,detail="Não foi possível criar o token de acesso, tente novamente mais tarde!")
    refresh_token = criar_token(usuario.id_usuario, timedelta(days=7),tipo="refresh")
    if not refresh_token:
        raise HTTPException(status_code=400,detail="Não foi possível criar o token de acesso, tente novamente mais tarde!")
    return UsuarioLoginResposta(
        login=usuario.login
        ,access_token=access_token
        ,refresh_token=refresh_token
    )

@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), db : Session =Depends(pegar_sessao)):
    usuario = autenticar_usuario(login=dados_formulario.username, senha=dados_formulario.password, db=db)
    if usuario:
        access_token = criar_token(usuario.id_usuario)
        return {
            "access_token":access_token,
            "token_type":"Bearer"
        }
    else:
        HTTPException(status_code=400, detail="Usuário não encontrado!")

@auth_router.get("/refresh-form")
async def use_refresh_token_form(usuario: Usuarios = Depends(verificar_token_oauth)):
    access_token = criar_token(usuario.id_usuario)
    return {
            "access_token":access_token,
            "token_type":"Bearer"
        }

@auth_router.get("/refresh")
async def use_refresh_token(refresh_token: str, db: Session = Depends(pegar_sessao)):
    usuario: Usuarios = verificar_token(refresh_token=refresh_token,db=db)
    access_token = criar_token(usuario.id_usuario)

    return {
            "access_token":access_token,
            "token_type":"Bearer"
        }

@auth_router.post("/resetpassword/email")
async def mandar_email(recuperar_senha_schema: RecuperarSenha, db: Session = Depends(pegar_sessao)):
    email = recuperar_senha_schema.email
    stmt = select(Usuarios).where(Usuarios.login == email)
    usuario = db.scalar(stmt)

    if not usuario:
        raise HTTPException(status_code=400, detail="Use o email cadastrado no site!")

    codigo = f"{secrets.randbelow(1000000):06}"

    mensagem = MessageSchema(
        subject="Recuperação de senha - Athena"
        ,recipients=[email]
        ,body="Seu código é: "+str(codigo)
        ,subtype="plain"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message=mensagem)
    except Exception as E:
        print(E)
        raise

    codigo_criptografado = bcrypt_context.hash(codigo)
    tempo_expiracao = datetime.utcnow() + timedelta(minutes=2)

    db.add(
        Recuperacoes_Senhas(
            login=email
            ,codigo=codigo_criptografado
            ,tempo_expiracao=tempo_expiracao
            ,usado=False
        )
    )

    db.commit()

    return JSONResponse(
        status_code=200
        ,content={
            "mensagem":"E-mail mandado com sucesso!"
        }
    )

@auth_router.post("/resetpassword/validation")
async def validar_codigo_resetar_senha(codigo_schema: RecuperarSenhaCodigo, db: Session = Depends(pegar_sessao)):
    email = codigo_schema.email
    codigo = codigo_schema.codigo
    stmt = select(Recuperacoes_Senhas).where(
        email==Recuperacoes_Senhas.login
        ,datetime.utcnow()<=Recuperacoes_Senhas.tempo_expiracao
        ,Recuperacoes_Senhas.usado==False
    )
    recuperacao = db.scalar(stmt)
    if not recuperacao:
        raise HTTPException(status_code=400, detail="Código inválido. Verifique se o código está correto e se o tempo não expirou!")
    elif not bcrypt_context.verify(codigo,recuperacao.codigo):
        raise HTTPException(status_code=400, detail="Código inválido. Verifique se o código está correto e se o tempo não expirou!")

    recuperacao.usado = True

    stmt = select(Usuarios).where(Usuarios.login == email)
    usuario = db.scalar(stmt)

    dic_inf = {
        "sub":str(usuario.id_usuario)
        ,"exp":datetime.utcnow() + timedelta(minutes=2)
        ,"type":"access"
    }

    db.commit()

    jwt_permissao = jwt.encode(dic_inf,SECRET_KEY,ALGORITHM)

    return {
        "token_validation":jwt_permissao
    }

@auth_router.post("/resetpassword/newpassword")
async def mudar_senha(senha_schema: RecuperarSenhaNovaSenha,token_validation: str, db: Session = Depends(pegar_sessao)):

    usuario = verificar_token(token_validation,db)
    senha_criptografada = bcrypt_context.hash(senha_schema.senha)
    usuario.senha = senha_criptografada

    db.commit()
    return JSONResponse(
        status_code=200
        ,content={
            "mensagem":"Senha alterada com sucesso!"
        }
    )
