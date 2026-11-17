from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
from passlib.context import CryptContext
from app.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_MINUTES

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def make_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"

def hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

def create_access_token(email: str) -> str:
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": email, "exp": expires}, JWT_SECRET, algorithm=JWT_ALGORITHM)
