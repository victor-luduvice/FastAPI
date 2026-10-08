from fastapi import APIRouter
from model import Usuario
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/")
async def home():
    """
    Rota para autenticação de usuários.
    """
    return {"message": "acesso a rota de autenticação", "autenticado": False}


@auth_router.post("/criar_conta")
async def criar_conta(email: str, senha: str, db: Session = None):
    if db is None:
        raise ValueError("É necessário informar a sessão do banco")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        return {"message": "Usuário já existe"}

    novo_usuario = Usuario(email=email, senha=senha)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"message": "Conta criada com sucesso", "usuario": novo_usuario} 

