from fastapi import FastAPI

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos():
    """
    Rota para listar pedidos.
    """

    return {"message": "List of orders"}