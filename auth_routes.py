from fastapi import APIRouter
from model import Usuario
from sqlalchemy.orm import Session
from dependencies import pegar_session

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/")
async def home():
    """
    Rota para autenticação de usuários.
    """
    return {"message": "acesso a rota de autenticação", "autenticado": False}


@auth_router.post("/criar_conta")
async def criar_conta(email: str, senha: str, nome: str, session = depends(pegar_session)):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        return {"message": "Usuário já existe."}
    else:
        novo_usuario = Usuario(email=email, senha=senha, nome=nome)
        session.add(novo_usuario)
        session.commit()
        return {"message": "Conta criada com sucesso."}

