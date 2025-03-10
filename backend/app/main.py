from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import search_routes, project_routes, debug_routes

app = FastAPI(
    title="Enterprise Search API",
    description="RAG-powered enterprise search backend",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # todo change it when deploying to production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
# app.include_router(search_routes.router, prefix="/api")
app.include_router(project_routes.router, prefix="/api")
app.include_router(debug_routes.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Enterprise Search Backend"}