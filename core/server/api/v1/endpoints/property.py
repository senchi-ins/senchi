import os
import asyncio
import hashlib
import jwt
import logging
import uuid
from datetime import datetime, timedelta

from server.api.v1.utils.utils import decode_jwt, hash_password, verify_password
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from typing import List, Optional
from pydantic import BaseModel

from schemas.property import (
    PropertyScores,
    PropertyDevices,
    PropertyAlerts,
    PropertyResponse,
    PropertyRequest,
    AddManagerPhoneNumberRequest,
    AddManagerPhoneNumberResponse
)


logger = logging.getLogger(__name__)

TAG = "Property"
PREFIX = "/property"

router = APIRouter()


@router.post("/list")
async def list_properties(
    property_request: PropertyRequest,
    request: Request,
) -> List[PropertyResponse]:
    properties = request.app.state.db.get_properties(property_request.user_id)
    if not properties:
        return []
    
    properties = [
        PropertyResponse(
            id=property['id'], 
            name=property['name'], 
            address=property['address'], 
            property_type=property['property_type'], 
            description=property['description'],
            scores=PropertyScores(
                overall=property['scores_overall'],
                internal=property['scores_internal'],
                external=property['scores_external']
            ),
            devices=PropertyDevices(
                connected=property['devices_connected'],
                total=property['devices_total']
            ),
            total_savings=property['total_savings'],
        ) for property in properties]
    return properties

@router.get("/alerts")
async def get_alerts(
    property_request: PropertyRequest,
    request: Request,
) -> PropertyAlerts:
    alerts = request.app.state.db.get_alerts(property_request.property_id)
    return alerts

@router.post("/add")
async def add_property(
    property_request: PropertyRequest,
    request: Request,
) -> PropertyResponse:
    # TODO: This also needs to allow people to set up a pi for the new property
    # Maybe its a + button on the page after going to the property page?
    success = request.app.state.db.add_property(property_request.user_id, property_request.property_name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add property")
    return PropertyResponse(id=property_request.user_id, name="New Property")

@router.post("/add-manager-phone-number")
async def add_manager_phone_number(
    property_request: AddManagerPhoneNumberRequest,
    request: Request,
) -> AddManagerPhoneNumberResponse:
    success = request.app.state.db.add_manager_phone_number(
        property_request.user_id,
        property_request.property_id, 
        property_request.phone_number,
        property_request.role
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add manager phone number")
    return {"success": True, "response": "Manager phone number added successfully"}