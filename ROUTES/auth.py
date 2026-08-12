from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from SCHEMAS import UsuarioCadastro, UsuarioCadastroResposta, UsuarioLoginResposta, UsuarioLogin, RecuperarSenha, RecuperarSenhaCodigo, RecuperarSenhaNovaSenha
from MODELS import Usuarios, Recuperacoes_Senhas
from DEPENDENCIES import pegar_sessao, verificar_token_oauth, verificar_token
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from CORE import bcrypt_context, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from dotenv import load_dotenv
import os
import secrets

RESET_PASSWORD_DEBUG = os.getenv("RESET_PASSWORD_DEBUG", "false").lower() == "true"
RESET_CODE_EXPIRE_MINUTES = 10


def criar_configuracao_email():
    email = os.getenv("ATHENA_EMAIL")
    senha = os.getenv("ATHENA_PASSWORD")
    if not email or not senha:
        return None
    return ConnectionConfig(
        MAIL_USERNAME=email,
        MAIL_PASSWORD=senha,
        MAIL_FROM=email,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
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
    email = recuperar_senha_schema.email.lower()
    stmt = select(Usuarios).where(Usuarios.login == email)
    usuario = db.scalar(stmt)

    if not usuario:
        raise HTTPException(status_code=400, detail="Use o email cadastrado no site!")

    codigo = f"{secrets.randbelow(1000000):06}"

    configuracao_email = criar_configuracao_email()
    if not RESET_PASSWORD_DEBUG:
        if not configuracao_email:
            raise HTTPException(
                status_code=503,
                detail="O envio de e-mail ainda não está configurado. Tente novamente mais tarde.",
            )

        mensagem = MessageSchema(
            subject="Recuperação de senha - Athena",
            recipients=[email],
            body="Seu código de recuperação Athena é: " + codigo,
            subtype="plain",
        )

        try:
            await FastMail(configuracao_email).send_message(message=mensagem)
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Não foi possível enviar o código por e-mail. Tente novamente mais tarde.",
            )

    codigo_criptografado = bcrypt_context.hash(codigo)
    tempo_expiracao = datetime.utcnow() + timedelta(minutes=RESET_CODE_EXPIRE_MINUTES)

    db.execute(
        update(Recuperacoes_Senhas)
        .where(
            Recuperacoes_Senhas.login == email,
            Recuperacoes_Senhas.usado == False,
        )
        .values(usado=True)
    )

    db.add(
        Recuperacoes_Senhas(
            login=email
            ,codigo=codigo_criptografado
            ,tempo_expiracao=tempo_expiracao
            ,usado=False
        )
    )

    db.commit()

    resposta = {
        "mensagem": "Código de recuperação gerado com sucesso!",
        "expires_in": RESET_CODE_EXPIRE_MINUTES * 60,
    }
    if RESET_PASSWORD_DEBUG:
        resposta["debug_code"] = codigo
        resposta["mensagem"] = "Código gerado para teste local."
    return resposta

@auth_router.post("/resetpassword/validation")
async def validar_codigo_resetar_senha(codigo_schema: RecuperarSenhaCodigo, db: Session = Depends(pegar_sessao)):
    email = codigo_schema.email.lower()
    codigo = codigo_schema.codigo
    stmt = (
        select(Recuperacoes_Senhas)
        .where(
            email == Recuperacoes_Senhas.login,
            datetime.utcnow() <= Recuperacoes_Senhas.tempo_expiracao,
            Recuperacoes_Senhas.usado == False,
        )
        .order_by(Recuperacoes_Senhas.id_recuperacao_senha.desc())
    )
    recuperacao = db.scalar(stmt)
    if not recuperacao:
        raise HTTPException(status_code=400, detail="Código inválido. Verifique se o código está correto e se o tempo não expirou!")
    elif not bcrypt_context.verify(codigo,recuperacao.codigo):
        raise HTTPException(status_code=400, detail="Código inválido. Verifique se o código está correto e se o tempo não expirou!")

    stmt = select(Usuarios).where(Usuarios.login == email)
    usuario = db.scalar(stmt)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    dic_inf = {
        "sub":str(usuario.id_usuario)
        ,"exp":datetime.utcnow() + timedelta(minutes=5)
        ,"type":"password_reset"
        ,"reset_id":recuperacao.id_recuperacao_senha
    }

    jwt_permissao = jwt.encode(dic_inf,SECRET_KEY,ALGORITHM)

    return {
        "token_validation":jwt_permissao
    }

@auth_router.post("/resetpassword/newpassword")
async def mudar_senha(senha_schema: RecuperarSenhaNovaSenha,token_validation: str, db: Session = Depends(pegar_sessao)):
    try:
        dados_token = jwt.decode(token_validation, SECRET_KEY, ALGORITHM)
        if dados_token.get("type") != "password_reset":
            raise JWTError("Tipo de token inválido")
        id_usuario = int(dados_token.get("sub"))
        id_recuperacao = int(dados_token.get("reset_id"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="A autorização para redefinir a senha expirou. Solicite um novo código.")

    usuario = db.get(Usuarios, id_usuario)
    recuperacao = db.get(Recuperacoes_Senhas, id_recuperacao)
    if (
        not usuario
        or not recuperacao
        or recuperacao.usado
        or recuperacao.login != usuario.login
        or recuperacao.tempo_expiracao < datetime.utcnow()
    ):
        raise HTTPException(status_code=401, detail="A autorização para redefinir a senha não é mais válida.")

    senha_criptografada = bcrypt_context.hash(senha_schema.senha)
    usuario.senha = senha_criptografada
    recuperacao.usado = True

    db.commit()
    return JSONResponse(
        status_code=200
        ,content={
            "mensagem":"Senha alterada com sucesso!"
        }
    )
