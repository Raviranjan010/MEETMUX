import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.errors import (
    AppError,
    app_error_handler,
    validation_error_handler,
    http_error_handler,
    generic_error_handler,
)
from app.api.routes import health, data
from app.api.routes import flights, gates, predictions, optimizer
from app.api.routes.endpoints import (
    conflicts_router,
    scenarios_router,
    reoptimize_router,
    analytics_router,
    alerts_router,
    cascade_router,
    explain_router,
    assignments_router,
    config_router,
    runways_router,
)
from app.ml.registry import registry

setup_logging(level="INFO")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: attempt to load ML model if present
    logger.info("Starting RunwayOptX API...")
    loaded = registry.load_latest()
    if loaded:
        logger.info(f"ML Model loaded successfully: version {registry.current_version}")
    else:
        logger.info("No ML model loaded at startup (will report ml_model_loaded=False)")
    yield
    logger.info("Shutting down RunwayOptX API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Predictive Air Traffic Delay & Airport Gate Scheduling Optimizer",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


# Exception Handlers per docs/API.md
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Include Routers - all under /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(flights.router, prefix="/api")
app.include_router(gates.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(optimizer.router, prefix="/api")
app.include_router(conflicts_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(reoptimize_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(cascade_router, prefix="/api")
app.include_router(explain_router, prefix="/api")
app.include_router(assignments_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(runways_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "online",
        "health_check": "/api/health",
        "docs": "/docs",
    }
