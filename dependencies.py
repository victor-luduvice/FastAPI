from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from model import SessionLocal, Usuario


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def pegar_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def criar_token(id_usuario: int) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": id_usuario, "exp": expira_em}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(pegar_session),
) -> Usuario:
    credenciais_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("user_id")
        if user_id is None:
            raise credenciais_exception
    except JWTError as exc:
        raise credenciais_exception from exc

    usuario = session.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise credenciais_exception

    return usuario


def verificar_admin(usuario: Usuario = Depends(obter_usuario_atual)) -> Usuario:
    if not usuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer perfil de administrador.",
        )
    return usuario
