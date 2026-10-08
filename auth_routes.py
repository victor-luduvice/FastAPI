from fastapi import APIRouter, Depends, HTTPException
from model import Usuario
from sqlalchemy.orm import Session
from dependencies import pegar_session
from main import bcrypt_context
from schemas import UsuarioSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/")
async def home():
    """
    Rota para autenticação de usuários.
    """
    return {"message": "acesso a rota de autenticação", "autenticado": False}


@auth_router.post("/criar_conta")
async def criar_conta( usuario_schema: UsuarioSchema, session = depends(pegar_session)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    else:
        hashed_senha = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(email=usuario_schema.email, senha=hashed_senha, nome=usuario_schema.nome, ativo=usuario_schema.ativo, admin=usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"message": f"Conta criada com sucesso.{usuario_schema.email}"}


@auth_router.post("/login")
async def login(usuario_schema: UsuarioSchema, session = Depends(pegar_session)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Email não cadastrado.")
    if not bcrypt_context.verify(usuario_schema.senha, usuario.senha):
        raise HTTPException(status_code=400, detail="Senha incorreta.")
    return {"message": f"Login realizado com sucesso.{usuario_schema.email}"}