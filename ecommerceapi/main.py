from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from ecommerceapi.db.database import get_db
from ecommerceapi.api.router import api_router

app = FastAPI()
app.include_router(api_router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
