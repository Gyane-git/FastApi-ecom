from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.utils.response import ok, err

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Liveness check")
def health():
    return {"status": "ok"}


@router.get("/db", summary="Database connectivity check")
def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return ok({"database": "connected"})
    except Exception:
        return err("Database connection failed")
