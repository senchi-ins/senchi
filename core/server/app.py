from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api.v1.api import api_router
import uvicorn


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://localhost:3000", 
        "http://localhost:8000", 
        "https://localhost:8000",
        "https://api.senchi.ca",
        "http://api.senchi.ca"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else [],
                "name": route.name if hasattr(route, 'name') else None
            })
    return {"routes": routes}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)