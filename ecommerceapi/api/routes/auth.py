from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.schemas.security import RegisterIn, TokenPair, MessageOut
from ecommerceapi.schemas.user import UserOut
from ecommerceapi.services.security_service import SecurityService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    return SecurityService.register(db, payload)


@auth_router.post("/login", response_model=TokenPair)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return SecurityService.login(db, email=form.username, password=form.password)


@auth_router.post("/refresh", response_model=TokenPair)
def refresh_tokens(refresh_token: str, db: Session = Depends(get_db)):
    return SecurityService.refresh_tokens(db, refresh_token)


@auth_router.post("/logout", response_model=MessageOut)
def logout(refresh_token: str, db: Session = Depends(get_db)):
    return SecurityService.logout(db, refresh_token)
