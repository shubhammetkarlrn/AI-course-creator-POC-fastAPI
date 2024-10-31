from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import process_routes

app = FastAPI(
    title="XML Processing API",
    description="API for processing XML files with OpenAI integration",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(process_routes.router, prefix="/api/v1")