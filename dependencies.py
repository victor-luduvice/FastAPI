from model import db
from sqlalchemy.orm import sessionmaker


def pegar_session():
    try:
        session = sessionmaker(bind=db)
        session = session()
        yield session
    finally:
        session.close()