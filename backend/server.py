from fastapi import FastAPI, APIRouter, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import Optional

# Define the root directory of the backend
ROOT_DIR = Path(__file__).parent

# Create the main FastAPI app
app = FastAPI()

# Create an API router with a /api prefix
api_router = APIRouter(prefix="/api")

# --- API Models ---

class ContactForm(BaseModel):
    """Pydantic model to validate the contact form data."""
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    message: str

# --- API Endpoints ---

@api_router.get("/")
async def root():
    """A simple root endpoint for the API."""
    return {"message": "Acencia API is running"}

@api_router.post("/contact")
async def submit_contact_form(contact_data: ContactForm):
    """
    Handles contact form submissions.
    This is a mock endpoint. It validates the data and returns a success
    response without saving the data to a database.
    """
    # In a real application, you would add logic here to
    # send an email or save the data.
    # For this version, we just log it to the console.
    logger.info(f"Received contact form submission from: {contact_data.name} ({contact_data.email})")
    logger.info(f"Message: {contact_data.message}")

    return {"status": "success", "message": "Nachricht erfolgreich gesendet"}

# Include the API router in the main app
app.include_router(api_router)

# --- Frontend Serving ---

# Define the path to the frontend build directory
# This assumes the frontend is in a sibling directory to the backend
FRONTEND_BUILD_DIR = ROOT_DIR.parent / "frontend" / "build"

# Check if the frontend build directory exists
if not FRONTEND_BUILD_DIR.exists():
    logger.error(f"Frontend build directory not found at: {FRONTEND_BUILD_DIR}")
    logger.error("Please build the frontend first by running 'npm run build' in the 'frontend' directory.")
else:
    # Mount the static files directory (for JS, CSS, images, etc.)
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_BUILD_DIR / "static"),
        name="static"
    )

    # Catch-all route to serve the frontend's index.html
    # This enables client-side routing in the React app
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Construct the full path to the requested file
        file_path = FRONTEND_BUILD_DIR / full_path

        # If the requested path is a file that exists, serve it.
        # Otherwise, serve the main index.html file.
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        else:
            return FileResponse(FRONTEND_BUILD_DIR / "index.html")

# --- Logging Configuration ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Server Startup ---

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")
    if not FRONTEND_BUILD_DIR.exists():
        logger.warning("Serving API only. Frontend not found.")
    else:
        logger.info(f"Serving frontend from: {FRONTEND_BUILD_DIR}")
