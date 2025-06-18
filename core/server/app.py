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
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to the API"} 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)