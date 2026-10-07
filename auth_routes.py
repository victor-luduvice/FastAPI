from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/")
async def autenticar():
    """
    Rota para autenticação de usuários.
    """
    return {"message": "acesso a rota de autenticação", "autenticado": false}
