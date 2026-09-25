import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AppException
from app.database.database import Base, engine
from app.ml.model_registry import model_registry

from app.api.routes.health import router as health_router
from app.api.routes.flights import router as flights_router
from app.api.routes.gates import router as gates_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.optimization import router as optimization_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables and Load ML Model into memory once
    logger.info("Starting up Airport Delay & Gate Scheduling Optimizer API...")
    Base.metadata.create_all(bind=engine)
    
    try:
        model_registry.load_model()
        logger.info("ML Delay Prediction Model successfully loaded into memory.")
    except Exception as e:
        logger.warning(f"ML Model could not be pre-loaded at startup: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Airport Delay & Gate Scheduling Optimizer API...")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer
    
    A production-grade decision-support system combining:
    - **Machine Learning (Scikit-Learn)** for runway and taxi delay prediction with non-leaking feature engineering.
    - **Operations Research (Google OR-Tools / Gurobi)** Mixed Integer Linear Programming (MILP) for optimal airport gate allocation.
    - **FastAPI** high-performance asynchronous REST API.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
has_wildcard = "*" in origins or any(o.strip() == "*" for o in origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if not has_wildcard else ["*"],
    allow_origin_regex=r"https?://.*" if has_wildcard else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response


# Centralized Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload or query parameters.",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred while processing the request.",
                "details": str(exc) if settings.ENVIRONMENT == "development" else None
            }
        }
    )


# Include API Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(flights_router, prefix="/api")
app.include_router(gates_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
app.include_router(optimization_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "status": "online"
    }
