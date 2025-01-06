import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

# Import the V1 router
from api.v1.router_v1 import router_v1


templates = Jinja2Templates(directory='templates')

# Create FastAPI application
app = FastAPI(
    title="Academic Reporting System",
    description="Comprehensive student performance reporting system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Include V1 router
app.include_router(router_v1)

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "Academic Reporting Engine is running"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )