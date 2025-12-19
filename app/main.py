from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import hashtags, users


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Project Python Engineer",
    docs_url="/docs",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hashtags.router, prefix="/hashtags", tags=["Hashtags"])
app.include_router(users.router, prefix="/users", tags=["Users"])
