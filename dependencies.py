from model import db
from sqlalchemy.orm import sessionmaker
from model import Usuario
from fastapi import Depends, HTTPException



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


def verificar_token(token: str, session = Depends(pegar_session)):
    #verificar se o token é válido
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
        if usuario is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido.")

    #extrair o id do usuário do token
    user_id: int = payload.get("user_id")

    usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
    return usuario