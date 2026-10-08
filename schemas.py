from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    email: str
    senha: str
    nome: str
    ativo: Optional[bool]  
    admin: Optional[bool] 

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    id: int
    descricao: str
    valor: float

    class Config:
        from_attributes = True