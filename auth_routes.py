from fastapi import APIRouter, Depends, HTTPException
from model import Usuario
from sqlalchemy.orm import Session
from dependencies import pegar_session
from main import bcrypt_context
from schemas import UsuarioSchema
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone


auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario: int):
    data_expiracao = datetime.now(timezone.utc) + timedelta(hours=1)
    dic_info = {"user_id": id_usuario, "exp": data_expiracao}
    token=jwt.encode(dic_info, "SECRET_KEY", algorithm="HS256")
    return token 

def autenticar_usuario(usuario: UsuarioSchema, session: Session):
    usuario_db = session.query(Usuario).filter(Usuario.email == usuario.email).first()
    if not usuario_db:
        raise HTTPException(status_code=400, detail="Email não cadastrado.")
    if not bcrypt_context.verify(usuario.senha, usuario_db.senha):
        raise HTTPException(status_code=400, detail="Senha incorreta.")
    return usuario_db


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