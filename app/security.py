from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # VULN #2 (JWT): не проверяем алгоритм подписи.
    # `options={"verify_signature": False}` позволяет подделать токен,
    # а отсутствие фиксации algorithms даёт алгоритмическую путаницу (alg=none / HS->RS).
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=None,                      # VULN #2: не ограничиваем алгоритмы
            options={"verify_signature": False},   # VULN #2: вообще не проверяем подпись
        )
        return payload
    except JWTError:
        return {}


def authenticate_user(db: Session, username: str, password: str):
    # VULN #1 (SQL Injection): конкатенация пользовательского ввода в SQL.
    # Пример payload: username = "admin' OR '1'='1' --"
    query = text(
        f"SELECT id, username, password_hash, is_admin FROM users "
        f"WHERE username = '{username}'"
    )
    row = db.execute(query).fetchone()
    if not row:
        return None
    if not verify_password(password, row.password_hash):
        return None
    return db.query(models.User).filter(models.User.id == row.id).first()
