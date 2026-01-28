from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.api.router import api_router
from ecommerceapi.core.exceptions import BaseAppException
from ecommerceapi.schemas.general import ErrorOut

app = FastAPI()
app.include_router(api_router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    error = ErrorOut(detail=exc.message)

    return JSONResponse(status_code=exc.status_code, content=error.model_dump())
