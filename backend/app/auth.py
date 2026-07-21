from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import Role, User

passwords=PasswordHash.recommended(); oauth2=OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
def hash_password(value: str)->str: return passwords.hash(value)
def token(user: User)->str:
    return jwt.encode({"sub":str(user.id),"exp":datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm="HS256")
def current_user(raw: str=Depends(oauth2), db: Session=Depends(get_db))->User:
    try: uid=int(jwt.decode(raw,settings.jwt_secret,algorithms=["HS256"])["sub"])
    except Exception as exc: raise HTTPException(401,"Invalid or expired access token") from exc
    user=db.get(User,uid)
    if not user or not user.active: raise HTTPException(401,"Inactive account")
    return user
def require(*roles: Role):
    def check(user: User=Depends(current_user)):
        if user.role not in roles: raise HTTPException(403,"This role cannot perform that action")
        return user
    return check
def scope_partner(user: User, partner_id: int):
    if user.role in (Role.partner_admin,Role.partner_technical) and user.partner_id != partner_id:
        raise HTTPException(403,"Partner tenant access denied")

