# API Endpoint System Documentation

## Overview

The API endpoint system is designed to be modular, maintainable, and scalable. It uses automatic discovery of endpoints and provides utilities for common patterns.

## Directory Structure

```
app/api/v1/
├── endpoints/           # Individual endpoint modules
├── utils/              # Utility functions and classes
│   └── endpoint_utils.py
├── api.py              # Main router and discovery logic
└── README.md           # This documentation
```

## Adding New Endpoints

### 1. Basic Endpoint Module

Create a new Python file in `app/api/v1/endpoints/` with the following structure:

```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# Module-level configuration
TAG = "Your Feature"  # For API documentation
PREFIX = "/your-feature"  # Base URL path

router = APIRouter()

@router.get("/")
async def your_endpoint(current_user = Depends(get_current_user)):
    return {"message": "Your endpoint"}
```

### 2. Custom Endpoints

Add custom endpoints specific to your feature:

```python
@router.post("/custom")
async def custom_endpoint(
    data: YourSchema,
    current_user = Depends(get_current_user)
):
    return await your_service.custom_operation(data)
```

## Example: Complete Endpoint Module

```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.api.v1.utils.endpoint_utils import (
    CRUDEndpointGenerator,
    handle_not_found,
    create_paginated_response
)

# Module configuration
TAG = "Example"
PREFIX = "/example"

router = APIRouter()
service = ExampleService()

# Custom endpoints
@router.get("/custom")
async def custom_endpoint(
    param: str,
    current_user = Depends(get_current_user)
):
    """
    Custom endpoint example.
    
    Args:
        param: Example parameter
        current_user: Authenticated user
    
    Returns:
        Custom response
    """
    return await service.custom_operation(param)
```

## Testing

1. Create test files in `tests/api/v1/endpoints/`
2. Test both standard and custom endpoints
3. Include authentication tests
4. Test error cases

## Common Patterns

1. **Pagination**
```python
@router.get("/")
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    items = await service.list(skip=skip, limit=limit)
    total = await service.count()
    return create_paginated_response(items, total, skip, limit)
```

2. **Batch Operations**
```python
@router.post("/batch")
async def batch_operation(
    items: List[ItemSchema],
    current_user = Depends(get_current_user)
):
    return await service.batch_process(items)
```

3. **Search/Filter**
```python
@router.get("/search")
async def search_items(
    query: str,
    filters: dict = None,
    current_user = Depends(get_current_user)
):
    return await service.search(query, filters)
``` 