from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import project_routes, debug_routes, message_routes, document_routes, whatsapp_routes

app = FastAPI(
    title="Enterprise Search API",
    description="RAG-powered enterprise search backend",
    version="0.1.0",
    debug= True
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

app.include_router(project_routes.router, prefix="")
app.include_router(debug_routes.router, prefix="")
app.include_router(message_routes.router, prefix="")
app.include_router(document_routes.router, prefix="")
app.include_router(whatsapp_routes.router, prefix="/whatsapp")

# mounting the oauth for integration
# from app.plugins.oauth_auth import app as oauth_auth_app
# app.mount("/oauth", oauth_auth_app)


@app.get("/app")
async def root():
    return {"message": "Enterprise Search Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7888, log_level="debug")