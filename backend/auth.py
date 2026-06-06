import bcrypt
import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta


load_dotenv()

def hash_password(password: str) -> str:
    bytes=password.encode('utf-8')
    salt=bcrypt.gensalt()
    encrypted_password=bcrypt.hashpw(bytes,salt)
    return encrypted_password.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    userBytes=plain.encode('utf-8')
    return bcrypt.checkpw(userBytes, hashed.encode('utf-8'))

def create_token(user_id: int, email: str) -> str:
    payload={'user_id':user_id,'email':email,'exp': datetime.utcnow() + timedelta(days=int(os.environ.get('JWT_EXPIRY_DAYS', 7)))}
    token=jwt.encode(payload,os.environ.get('JWT_SECRET'),algorithm='HS256')
    return token

def decode_token(token: str) -> dict:
    return jwt.decode(token,os.environ.get('JWT_SECRET') , algorithms=['HS256'])
