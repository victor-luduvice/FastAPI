from model import db
from sqlalchemy.orm import sessionmaker


def pegar_session():
    try:
        session = sessionmaker(bind=db)
        session = session()
        yield session
    finally:
        session.close()


class loginSchema:
    email: str
    senha: str
    class Config:
        from_attributes = True