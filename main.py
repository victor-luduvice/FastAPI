from fastapi import FastAPI
from sqlalchemy import inspect, text

from auth_routes import auth_router
from model import base, db
from order_routes import order_router


def normalizar_schema_banco() -> None:
    inspector = inspect(db)
    if "itens" not in inspector.get_table_names():
        return

    colunas = [coluna["name"] for coluna in inspector.get_columns("itens")]
    if "tamanho" not in colunas and "tamanhho" in colunas:
        with db.begin() as conn:
            conn.execute(text("ALTER TABLE itens RENAME COLUMN tamanhho TO tamanho"))


app = FastAPI(
    title="Pizza Delivery API",
    description="API para gestão de pedidos de pizza com autenticação JWT e níveis de acesso.",
    version="1.0.0",
)

base.metadata.create_all(bind=db)
normalizar_schema_banco()

app.include_router(auth_router)
app.include_router(order_router)

# para rodar o servidor: uvicorn main:app --reload