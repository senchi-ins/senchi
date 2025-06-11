from fastapi import APIRouter
import importlib
import pkgutil
from pathlib import Path
from core.config import settings

api_router = APIRouter()

def discover_routers():
    """
    Automatically discover and include all routers from the endpoints package.
    Each module should export a router object named 'router'.
    """
    endpoints_path = Path(__file__).parent / "endpoints"
    for _, name, _ in pkgutil.iter_modules([str(endpoints_path)]):
        try:
            module = importlib.import_module(f"api.{settings.VERSION}.endpoints.{name}")
            if hasattr(module, "router"):
                router = getattr(module, "router")
                
                tag = getattr(module, "TAG", name.replace("_", " ").title())
                
                prefix = getattr(module, "PREFIX", f"/{name}")
                api_router.include_router(router, prefix=prefix, tags=[tag])
                
        except Exception as e:
            print(f"Warning: Could not load router from {name}: {str(e)}")

discover_routers() 