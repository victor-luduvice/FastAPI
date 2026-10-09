from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import bcrypt_context
from dependencies import criar_token, obter_usuario_atual, pegar_session
from model import Usuario
from schemas import Token, UsuarioCreate, UsuarioLogin, UsuarioResponse


auth_router = APIRouter(prefix="/auth", tags=["auth"])


def autenticar_usuario(usuario_data: UsuarioLogin, session: Session):
    usuario_db = session.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if not usuario_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email não cadastrado.")
    if not bcrypt_context.verify(usuario_data.senha, usuario_db.senha):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha incorreta.")
    return usuario_db


@auth_router.get("/")
async def home():
    return {"message": "Acesso à rota de autenticação", "autenticado": False}


@auth_router.post("/criar_conta", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_conta(usuario_schema: UsuarioCreate, session: Session = Depends(pegar_session)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado.")

    hashed_senha = bcrypt_context.hash(usuario_schema.senha)
    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=hashed_senha,
        ativo=usuario_schema.ativo,
        admin=usuario_schema.admin,
    )
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return novo_usuario


@auth_router.post("/login", response_model=Token)
async def login(usuario_schema: UsuarioLogin, session: Session = Depends(pegar_session)):
    usuario = autenticar_usuario(usuario_schema, session)
    token = criar_token(usuario.id)
    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(obter_usuario_atual)):
    return usuario
