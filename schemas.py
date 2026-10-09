from typing import List, Optional

from pydantic import BaseModel, Field


class UsuarioBase(BaseModel):
    nome: str
    email: str
    ativo: bool = True
    admin: bool = False

    class Config:
        from_attributes = True


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioLogin(BaseModel):
    email: str
    senha: str


class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ItemPedidoBase(BaseModel):
    sabor: str
    tamanho: str
    quantidade: int = Field(default=1, ge=1)
    preco: float = Field(default=0.0, ge=0)


class ItemPedidoCreate(ItemPedidoBase):
    pass


class ItemPedidoResponse(ItemPedidoBase):
    id: int
    pedido_id: int

    class Config:
        from_attributes = True


class PedidoCreate(BaseModel):
    itens: List[ItemPedidoCreate] = []
    status: Optional[str] = "PENDENTE"


class PedidoResponse(BaseModel):
    id: int
    usuario_id: int
    status: str
    preco: float
    itens: List[ItemPedidoResponse] = []

    class Config:
        from_attributes = True
