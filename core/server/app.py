

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from api.v1.api import api_router
from db.pg import PostgresDB
from db.rds import RedisDB

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = PostgresDB()
    redis_db = RedisDB()
    try:
        app.state.db = db
        app.state.redis_db = redis_db
        redis_db.connect()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
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
