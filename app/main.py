import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import brands, categories, products, vendors, reviews, health
from app.core.config import get_settings
from app.core.logging import setup_logging, RequestLoggingMiddleware

settings = get_settings()
setup_logging(settings.DEBUG)
log = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Scalable ecommerce REST API for the ecomTest_db MySQL database.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Error") if isinstance(exc.detail, dict) else "Error"
    return JSONResponse(status_code=exc.status_code, content={"success": False, "data": None, "message": message})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"success": False, "data": None, "message": "Validation error", "errors": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"success": False, "data": None, "message": "Internal server error"})


app.include_router(health.router)
app.include_router(products.router, prefix="/api/v1")
app.include_router(brands.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(vendors.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")

from fastapi.staticfiles import StaticFiles
from app.utils.upload import UPLOAD_DIR
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
