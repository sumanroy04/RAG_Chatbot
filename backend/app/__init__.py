from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.errors import http_exception_handler
from backend.app.extensions import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    
    # Setup vectorstore (cached at module level)
    from backend.chatbot.knowledge_base import setup_vectorstore
    app.state.vectorstore = setup_vectorstore()
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="Patronus AI",
        description="Mental health support chatbot API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Include routers
    from backend.auth.routes import auth_router
    from backend.api.routes.chat import chat_router
    from backend.api.routes.appointments import appointments_router
    from backend.api.routes.resources import resources_router
    from backend.api.routes.crisis import crisis_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(chat_router, tags=["Chat"])
    app.include_router(appointments_router, prefix="/api/appointments", tags=["Appointments"])
    app.include_router(resources_router, prefix="/api/resources", tags=["Resources"])
    app.include_router(crisis_router, prefix="/api/crisis", tags=["Crisis Support"])

    return app
