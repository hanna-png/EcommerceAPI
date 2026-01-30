from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.api.router import api_router
from ecommerceapi.core.exceptions import (
    BaseAppException,
    ResourceNotFoundException,
    ValidationException,
    UnauthorizedException,
)
from ecommerceapi.schemas.general import ErrorOut
from ecommerceapi.core.logging import logger

app = FastAPI()
app.include_router(api_router)
logger.info("Application started")


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.exception_handler(BaseAppException)
def app_exception_handler(request: Request, exc: BaseAppException):
    error = ErrorOut(detail=exc.message)
    logger.error(
        f"{exc.__class__.__name__} | {request.method} {request.url.path} | {exc.message}"
    )

    if isinstance(exc, ResourceNotFoundException):
        status_code = 404
    elif isinstance(exc, ValidationException):
        status_code = 400
    elif isinstance(exc, UnauthorizedException):
        status_code = 401
    else:
        status_code = 500

    return JSONResponse(status_code=status_code, content=error.model_dump())


@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error | {request.method} {request.url.path}", exc_info=exc)
    error = ErrorOut(detail="Unexpected error occurred.")
    return JSONResponse(status_code=500, content=error.model_dump())
