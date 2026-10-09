from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


db = create_engine("sqlite:///banco.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=db, autocommit=False, autoflush=False, expire_on_commit=False)
base = declarative_base()


class Usuario(base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    senha = Column(String, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)

    pedidos = relationship("Pedido", back_populates="usuario", cascade="all, delete-orphan", lazy="selectin")

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin


class Pedido(base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(String, default="PENDENTE", nullable=False)
    preco = Column(Float, default=0.0, nullable=False)

    usuario = relationship("Usuario", back_populates="pedidos", lazy="selectin")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan", lazy="selectin")

    def __init__(self, usuario_id, status="PENDENTE", preco=0.0):
        self.usuario_id = usuario_id
        self.status = status
        self.preco = preco


class ItemPedido(base):
    __tablename__ = "itens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    sabor = Column(String, nullable=False)
    tamanho = Column(String, nullable=False)
    preco = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="itens", lazy="selectin")

    def __init__(self, pedido_id, quantidade, sabor, tamanho, preco):
        self.pedido_id = pedido_id
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco = preco
