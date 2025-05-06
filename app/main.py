# main.py: Entry point for the FastAPI application
from fastapi import FastAPI
from app.routers import field_router, irrigation_router
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

# Initialize FastAPI app
app = FastAPI(
    title="Smart Agriculture Backend",
    description="Backend for AI-powered crop and irrigation recommendations",
    version="1.0.0"
)

# Serve static files from the 'front-end/static' directory
frontend_dir = os.path.join(os.path.dirname(__file__), "../front-end")

# Serve static files from the 'front-end' directories
app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
app.mount("/img", StaticFiles(directory=os.path.join(frontend_dir, "img")), name="img")
app.mount("/lib", StaticFiles(directory=os.path.join(frontend_dir, "lib")), name="lib")
app.mount("/scss", StaticFiles(directory=os.path.join(frontend_dir, "scss")), name="scss")

# Route to serve the index.html as the landing page
@app.get("/", response_class=HTMLResponse)
async def read_index():
    # Path to the index.html file
    index_path = os.path.join(frontend_dir, "index.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/index.html", response_class=HTMLResponse)
async def read_index():
    # Path to the index.html file
    index_path = os.path.join(frontend_dir, "index.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/service.html", response_class=HTMLResponse)
async def read_index():
    # Path to the index.html file
    index_path = os.path.join(frontend_dir, "service.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/about.html", response_class=HTMLResponse)
async def read_index():
    # Path to the index.html file
    index_path = os.path.join(frontend_dir, "about.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

# Include routers for field and irrigation endpoints
app.include_router(field_router.router, prefix="/api/v1/fields", tags=["Fields"])
app.include_router(irrigation_router.router, prefix="/api/v1/irrigation", tags=["Irrigation"])
