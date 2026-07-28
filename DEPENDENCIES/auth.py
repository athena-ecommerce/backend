from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from CORE import SECRET_KEY, ALGORITHM, oauth2_schema
from DEPENDENCIES.session import pegar_sessao
from MODELS import Usuarios

# OBS: Essa dependência decodifica o token JWT enviado pelo usuário e busca ele no banco.
# Ainda não existe uma rota de login que gere o token (com "sub" = id_usuario),
# então essa função só vai funcionar de verdade quando essa rota existir.


def usuario_logado(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(pegar_sessao),
) -> Usuarios:
    excecao_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = payload.get("sub")

        if id_usuario is None:
            raise excecao_credenciais

    except JWTError:
        raise excecao_credenciais

    usuario = db.get(Usuarios, int(id_usuario))

    if usuario is None:
        raise excecao_credenciais

    return usuario
