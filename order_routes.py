from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import obter_usuario_atual, pegar_session, verificar_admin
from model import ItemPedido, Pedido, Usuario
from schemas import ItemPedidoCreate, PedidoCreate, PedidoResponse

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@order_router.get("/", response_model=list[PedidoResponse])
async def listar_pedidos(
    usuario: Usuario = Depends(obter_usuario_atual),
    session: Session = Depends(pegar_session),
):
    if usuario.admin:
        pedidos = session.query(Pedido).all()
    else:
        pedidos = session.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()
    return pedidos


@order_router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def criar_pedido(
    pedido_schema: PedidoCreate,
    usuario: Usuario = Depends(obter_usuario_atual),
    session: Session = Depends(pegar_session),
):
    novo_pedido = Pedido(usuario_id=usuario.id, status=pedido_schema.status or "PENDENTE", preco=0.0)
    session.add(novo_pedido)
    session.flush()

    total_pedido = 0.0
    for item in pedido_schema.itens:
        item_pedido = ItemPedido(
            pedido_id=novo_pedido.id,
            quantidade=item.quantidade,
            sabor=item.sabor,
            tamanho=item.tamanho,
            preco=item.preco,
        )
        novo_pedido.itens.append(item_pedido)
        total_pedido += item.quantidade * item.preco

    novo_pedido.preco = total_pedido
    session.commit()
    session.refresh(novo_pedido)
    return novo_pedido


@order_router.post("/{pedido_id}/itens", response_model=PedidoResponse)
async def adicionar_item_no_pedido(
    pedido_id: int,
    item_schema: ItemPedidoCreate,
    usuario: Usuario = Depends(obter_usuario_atual),
    session: Session = Depends(pegar_session),
):
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if not usuario.admin and pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para alterar este pedido.")

    novo_item = ItemPedido(
        pedido_id=pedido.id,
        quantidade=item_schema.quantidade,
        sabor=item_schema.sabor,
        tamanho=item_schema.tamanho,
        preco=item_schema.preco,
    )
    pedido.itens.append(novo_item)
    pedido.preco += item_schema.quantidade * item_schema.preco
    session.commit()
    session.refresh(pedido)
    return pedido


@order_router.patch("/{pedido_id}/finalizar", response_model=PedidoResponse)
async def finalizar_pedido(
    pedido_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    session: Session = Depends(pegar_session),
):
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if not usuario.admin and pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Você não pode finalizar este pedido.")

    pedido.status = "FINALIZADO"
    session.commit()
    session.refresh(pedido)
    return pedido


@order_router.get("/admin", response_model=list[PedidoResponse])
async def listar_pedidos_admin(
    usuario: Usuario = Depends(verificar_admin),
    session: Session = Depends(pegar_session),
):
    pedidos = session.query(Pedido).all()
    return pedidos
