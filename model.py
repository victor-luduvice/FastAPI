from sqlalchemy import create_engine, Column, Integer, String, boolean, ForeignKey, float
from sqlalchemy.orm import declarative_base
from sqlalchemy.utils import ChoiceType

db = create_engine("sqlite:///banco.db")

base = declarative_base()

class Usuario(base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String)
    email = Column("email", String, nullable=False, unique=True)
    senha = Column("senha", String)
    ativo = Column("ativo", boolean)
    admin = Column("admin", boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

class Pedido(base):
    __tablename__ = "pedidos"

    STATUS_PEDIDOS = ("PENDENTE", "PENDENTE"), ("EM_ANDAMENTO", "EM_ANDAMENTO"), ("FINALIZADO", "FINALIZADO")

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    status = Column("status", String, ChoiceType(STATUS_PEDIDOS))
    preco = Column("preco", float)

    def __init__(self, usuario_id, status=PENDENTE, preco=0):
        self.usuario_id = usuario_id
        self.status = status
        self.preco = preco


 class ItemPedido(base):
    __tablename__ = "itens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quantidade = Column(Integer, ForeignKey("pedidos.id"))
    sabor = Column("sabor", String)
    tamanhho = Column("tamanhho", float)
    preco = Column("preco", float)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))

    def __init__(self, pedido_id, quantidade, sabor, tamanhho, preco):
        self.pedido_id = pedido_id
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanhho = tamanhho
        self.preco = preco       
