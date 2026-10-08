from fastapi import FastAPI
from passlib.context import CryptContext
from doteenv import load_dotenv
import os

load_dotenv()

Secret_key = os.getenv("SECRET_KEY")

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)

# para rodar o servidor: uvicorn main:app --reload