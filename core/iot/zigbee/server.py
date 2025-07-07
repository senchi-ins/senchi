from contextlib import asynccontextmanager
import os
import sys
import json
import asyncio
import logging
from typing import Union
from datetime import datetime

import uvicorn
import pandas as pd
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from monitor.config import settings
from monitor.models import (
    Device,
    DeviceType,
    NotificationResponse,
    LeakSensorResponse,
    NOTIFICATION_TYPES,
)
from monitor.monitor import Monitor
from monitor.utils import get_all_model_fields

logger = logging.getLogger(__name__)

app_state = {
    "devices": {},
    "websocket_connections": [],
    "mqtt_client": None,
    "notification_config": None,
    "active_leaks": set(),
    "notification_queue": asyncio.Queue()
}

def init_db():
    """
    Initialize the database connection.

    Note: Currently uses pd.df and writed to a csv file.
    """
    # 2 tables are needed:
    # 1. devices
    # 2. notifications / device events
    # Temp database
    database = {
        "devices": pd.DataFrame(columns=list(Device.model_fields.keys())),
        "notifications": pd.DataFrame(columns=get_all_model_fields(NOTIFICATION_TYPES)),
    }
    return database

db = init_db()
mqtt_monitor = Monitor(app_state, db)


@asynccontextmanager
async def lifespan(app: FastAPI):

    loop = asyncio.get_running_loop()
    mqtt_monitor.loop = loop
    mqtt_monitor.start()
    
    logging.info("Home API Server started with integrated MQTT monitoring")
    yield
    
    mqtt_monitor.stop()
    logging.info("Home API Server stopped")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOWED_CREDENTIALS,
    allow_headers=settings.ALLOWED_HEADERS,
    allow_methods=settings.ALLOWED_METHODS,
)

@app.get("/")
async def root():
    return {
        "message": "Home Automation API with Integrated Notifications",
        "version": "1.0.0",
        "mqtt_connected": mqtt_monitor.connected,
        "active_leaks": len(app_state["active_leaks"]),
        "total_devices": len(app_state["devices"])
    }


@app.get("/devices")
async def get_devices():
    """Get all devices"""
    return list(app_state["devices"].values())


@app.post("/zigbee/permit-join")
async def permit_join(duration: int = 60):
    """Allow new devices to join"""
    if mqtt_monitor.connected:
        mqtt_monitor.client.publish(
            "zigbee2mqtt/bridge/request/permit_join",
            json.dumps({"time": duration})
        )
        return {"message": f"Permit join enabled for {duration} seconds"}
    else:
        raise HTTPException(status_code=503, detail="MQTT not connected")
    

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app_state["websocket_connections"].append(websocket)
    
    try:
        for device_id, device in app_state["devices"].items():
            message = {
                "type": "device_update",
                "device_id": device_id,
                "data": device.status,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(message))
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        app_state["websocket_connections"].remove(websocket)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mqtt_connected": mqtt_monitor.connected,
        "devices": len(app_state["devices"]),
        "active_leaks": len(app_state["active_leaks"]),
        "websocket_connections": len(app_state["websocket_connections"])
    }

if __name__ == "__main__":

    # Extra debug logging for development
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )
    
    logging.getLogger().setLevel(logging.DEBUG)
    
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")