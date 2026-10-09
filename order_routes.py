from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException
from model import Pedido
from sqlalchemy.orm import Session
from dependencies import pegar_session
from schemas import PedidoSchema

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos():
    """
    Rota para listar pedidos.
    """

    return {"Voce está na rota de pedidos", "pedidos"}

@order_router.post("/pedido")   
async def criar_pedido(PedidoSchema: PedidoSchema, session = Depends(pegar_session)):
    pedido = session.query(Pedido).filter(Pedido.id == PedidoSchema.id).first()
    if pedido:
        raise HTTPException(status_code=400, detail="Pedido já cadastrado.")
    else:
        novo_pedido = Pedido(id=PedidoSchema.id, descricao=PedidoSchema.descricao, valor=PedidoSchema.valor)
        session.add(novo_pedido)
        session.commit()
        return {"message": f"Pedido criado com sucesso.{PedidoSchema.id}"}  


@order_router.get("refrestoken")
async def refresh_token(token):
    usuario = verificar_token(token)
    acesso_token = criar_token(usuario.id)
    return {"access_token": acesso_token, "token_type": "bearer"}