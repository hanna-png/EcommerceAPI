from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ecommerceapi.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> SessionLocal:
    """
    Creates a new database session for single request, returns it to the caller and closes it safely.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
