from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from schemas.quotes import Quote


TAG = "Quote"
PREFIX = "/quote"

router = APIRouter()

# NOTE:For testing only
@router.get("/")
async def get_home_quote():
    """Get a quote"""
    return {"This quote is for a home!"}
