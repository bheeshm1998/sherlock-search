import logging
import os
import secrets

from dotenv import set_key, dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import project_routes, debug_routes, message_routes, document_routes, whatsapp_routes, auth_routes

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
app.include_router(auth_routes.router, prefix="")
app.include_router(whatsapp_routes.router, prefix="/whatsapp")

# mounting the oauth for integration
# from app.plugins.oauth_auth import app as oauth_auth_app
# app.mount("/oauth", oauth_auth_app)

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[logging.StreamHandler()],  # Log to the console
)

logger = logging.getLogger(__name__)


# Check and generate secret key if not exists
def generate_secret_key():
    # Path to your .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')

    # Load existing environment variables
    existing_env = dotenv_values(env_path)

    # Check if JWT_SECRET_KEY already exists
    if 'JWT_SECRET_KEY' not in existing_env or not existing_env['JWT_SECRET_KEY']:
        # Generate a new secret key
        new_secret_key = secrets.token_hex(32)

        # Append only the JWT_SECRET_KEY to the .env file
        with open(env_path, 'a') as f:
            # Add a newline first if the file doesn't end with a newline
            f.write('\n' if not existing_env else '')
            f.write(f'JWT_SECRET_KEY={new_secret_key}\n')

        print("Generated a new JWT secret key.")
        return new_secret_key

    print("JWT secret key already exists.")
    return existing_env['JWT_SECRET_KEY']

@app.get("/app")
async def root():
    logger.debug("Root endpoint accessed")
    return {"message": "Enterprise Search Backend"}


if __name__ == "__main__":
    import uvicorn
    generate_secret_key()
    uvicorn.run(app, host="0.0.0.0", port=7888, log_level="debug")