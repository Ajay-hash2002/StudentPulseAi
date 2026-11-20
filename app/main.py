import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database.session import engine, Base, SessionLocal
import app.database.models  # Ensure models are registered on Base.metadata
from app.database.seed import seed_database
from app.schemas.envelope import ApiResponse, ErrorDetail

# API Routers
from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.assessments import router as assessments_router
from app.api.catalog import router as catalog_router
from app.api.career_goals import router as goals_router
from app.api.analysis import router as analysis_router
from app.api.action_plans import router as action_plans_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed demo data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Evidence → Insight → Action | AI-Powered Student Success & Career-Readiness Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"
    request.state.request_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# CORS Middleware (Restricted to known origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom Exception Handlers for Envelope Consistency
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", f"req-{uuid.uuid4().hex[:12]}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Please check the submitted information.",
                "details": exc.errors()
            },
            "request_id": req_id
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    req_id = getattr(request.state, "request_id", f"req-{uuid.uuid4().hex[:12]}")
    code = "HTTP_ERROR"
    if exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
    elif exc.status_code == 404:
        code = "NOT_FOUND"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": exc.detail
            },
            "request_id": req_id
        }
    )

# Health endpoints
@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check(request: Request):
    req_id = getattr(request.state, "request_id", f"req-{uuid.uuid4().hex[:12]}")
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "project": settings.PROJECT_NAME,
            "tagline": settings.TAGLINE,
            "version": "1.0.0",
            "stage": "MSE-2 Prototype Baseline",
            "team": "Byte Force (KIET)"
        },
        "request_id": req_id
    }

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(students_router, prefix=settings.API_V1_PREFIX)
app.include_router(assessments_router, prefix=settings.API_V1_PREFIX)
app.include_router(catalog_router, prefix=settings.API_V1_PREFIX)
app.include_router(goals_router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)
app.include_router(action_plans_router, prefix=settings.API_V1_PREFIX)

# Static Frontend Files
static_dir = settings.BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
