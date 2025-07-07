# user_manager.py - FastAPI service for MQTT user management
import subprocess
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MQTT User Manager", version="1.0.0")

PASSWD_FILE = "/mosquitto_passwd"


class AddUserRequest(BaseModel):
    username: str
    password: str

class RemoveUserRequest(BaseModel):
    username: str

class UserResponse(BaseModel):
    username: str
    status: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "MQTT User Manager is running", "version": "1.0.0"}

@app.post("/users", response_model=UserResponse)
async def add_user(request: AddUserRequest):
    """Add a new MQTT user"""
    try:
        logger.info(f"Adding MQTT user: {request.username}")
        
        subprocess.run([
            'mosquitto_passwd', '-b', PASSWD_FILE, 
            request.username, request.password
        ], capture_output=True, text=True, check=True)
        
        # This reloads the mosquitto config to pick up new user without restarting the container
        reload_result = subprocess.run(['pkill', '-HUP', 'mosquitto'], 
                                     capture_output=True, text=True)
        
        if reload_result.returncode == 0:
            logger.info(f"Successfully added user {request.username} and reloaded mosquitto")
        else:
            logger.warning(f"Added user {request.username} but mosquitto reload may have failed")
        
        return UserResponse(username=request.username, status="added")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add user {request.username}: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Failed to add user: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error adding user {request.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.delete("/users/{username}", response_model=UserResponse)
async def remove_user(username: str):
    """Remove an MQTT user"""
    try:
        logger.info(f"Removing MQTT user: {username}")
        
        subprocess.run([
            'mosquitto_passwd', '-D', PASSWD_FILE, username
        ], capture_output=True, text=True, check=True)
        
        reload_result = subprocess.run(['pkill', '-HUP', 'mosquitto'], 
                                     capture_output=True, text=True)
        
        if reload_result.returncode == 0:
            logger.info(f"Successfully removed user {username} and reloaded mosquitto")
        else:
            logger.warning(f"Removed user {username} but mosquitto reload may have failed")
            
        return UserResponse(username=username, status="removed")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove user {username}: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Failed to remove user: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error removing user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/users")
async def list_users():
    """List all MQTT users"""
    try:
        if not os.path.exists(PASSWD_FILE):
            return {"users": [], "total": 0}
            
        with open(PASSWD_FILE, 'r') as f:
            lines = f.readlines()
            
        users = []
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                username = line.split(':')[0]
                users.append(username)
                
        return {"users": users, "total": len(users)}
        
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check for the service"""
    try:
        mosquitto_check = subprocess.run(['pgrep', 'mosquitto'], 
                                       capture_output=True, text=True)
        mosquitto_status = "running" if mosquitto_check.returncode == 0 else "stopped"
        
        passwd_exists = os.path.exists(PASSWD_FILE)
        
        return {
            "status": "healthy",
            "mosquitto": mosquitto_status,
            "password_file": "exists" if passwd_exists else "missing"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MQTT User Manager API on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")