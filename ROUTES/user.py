from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from httpx import AsyncClient

from DEPENDENCIES import verificar_token, pegar_sessao
from MODELS import Usuarios, Enderecos
from SCHEMAS.user_schema import UserResponse
from SCHEMAS.address_schema import EnderecoCompleto, EnderecoResponse, EnderecoCepResponse

user_router = APIRouter(prefix="/user", tags=["Usuarios"])


@user_router.get("/profile", response_model=UserResponse)
async def buscar_informacoes_usuario(db: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    info_usuario = (
        db.query(Usuarios)
        .options(joinedload(Usuarios.enderecos))
        .filter(Usuarios.id_usuario == usuario.id_usuario)
        .first()
    )
    
    if not info_usuario:
        raise HTTPException(status_code=404, detail="Usuário não logado ou não encontrado.")
    return info_usuario


@user_router.post("/adicionar-endereco", response_model=EnderecoResponse)
async def adicionar_endereco_usuario(endereco_schema: EnderecoCompleto, db: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    id_usuario = usuario.id_usuario
    
    novo_endereco = Enderecos(
        id_usuario=id_usuario,
        rua=endereco_schema.rua,
        bairro=endereco_schema.bairro,
        estado=endereco_schema.estado,
        numero=endereco_schema.numero,
        complemento=endereco_schema.complemento,
        cep=endereco_schema.cep
    )
    
    db.add(novo_endereco)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível cadastrar o endereço.")
    
    db.refresh(novo_endereco)
    return novo_endereco


@user_router.get("/cep/{cep}", response_model=EnderecoCepResponse)
async def buscar_endereco_cep(cep: str):
    # Fazendo requisição
    async with AsyncClient() as client:
        response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
        dados_endereco = response.json()
    
    if dados_endereco.get("erro"):
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    
    endereco = Enderecos(
        rua=dados_endereco.get("logradouro"),
        bairro=dados_endereco.get("bairro"),
        estado=dados_endereco.get("uf"),
        complemento=dados_endereco.get("complemento"),
        cep=dados_endereco.get("cep")
    )
    
    return endereco