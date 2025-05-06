from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.routers import field_router
from app.models import FieldRequest, Location
import os
import json
import logging

# Initialize FastAPI app
app = FastAPI(
    title="Smart Agriculture Backend",
    description="Backend for AI-powered crop and irrigation recommendations",
    version="1.0.0"
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Serve static files from the 'front-end' directory
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
    index_path = os.path.join(frontend_dir, "index.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/index.html", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(frontend_dir, "index.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/results.html", response_class=HTMLResponse)
async def read_results(lat: float = Query(None), lng: float = Query(None)):
    index_path = os.path.join(frontend_dir, "results.html")
    with open(index_path, "r") as file:
        html_content = file.read()

    # If lat and lng are provided, call field_router.create_field
    response_data = {}
    if lat is not None and lng is not None:
        try:
            field_request = FieldRequest(location=Location(latitude=lat, longitude=lng), user_id="default_user")
            response = await field_router.create_field(field_request)
            response_data = response.dict()
            logger.info(f"fieldResponse: {response_data}")
        except Exception as e:
            response_data = {"error": str(e)}
            logger.error(f"Error creating field response: {str(e)}")

    # Embed response data in HTML
    html_content = html_content.replace(
        '</head>',
        f'<script>window.fieldResponse = {json.dumps(response_data)};</script></head>'
    )
    return HTMLResponse(content=html_content)

@app.get("/service.html", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(frontend_dir, "service.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/about.html", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(frontend_dir, "about.html")
    with open(index_path, "r") as file:
        return HTMLResponse(content=file.read())

# Include field router
app.include_router(field_router.router, prefix="/api/v1/fields", tags=["Fields"])