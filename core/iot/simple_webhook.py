from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
from datetime import datetime
import uvicorn

app = FastAPI(title="Simple Webhook Server", description="A simple webhook server that prints POST requests to console")

@app.post("/")
async def webhook(request: Request):
    """Handle incoming webhook POST requests and print them to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n=== Webhook Received at {timestamp} ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    
    # Get request body
    body = await request.body()
    try:
        # Try to parse as JSON
        json_body = await request.json()
        print(f"JSON Body: {json.dumps(json_body, indent=2)}")
    except:
        # If not JSON, print as raw text
        print(f"Raw Body: {body.decode('utf-8')}")
    
    print("=" * 50)
    
    # Return success response
    return JSONResponse(content={"status": "success", "message": "Webhook received"}, status_code=200)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(content={"status": "healthy", "message": "Webhook server is running"}, status_code=200)

@app.post("/test")
async def test_webhook():
    """Test endpoint to simulate a SwitchBot webhook payload"""
    test_payload = {
        "eventType": "deviceReport",
        "eventVersion": "1",
        "context": {
            "deviceType": "Bot",
            "deviceMac": "test-device-mac",
            "deviceName": "Test SwitchBot"
        },
        "eventTime": "2024-01-01T12:00:00.000Z",
        "eventData": {
            "deviceId": "test-device-id",
            "command": "turnOn",
            "parameter": "default"
        }
    }
    
    print(f"\n=== Test Webhook Payload ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print("=" * 50)
    
    return JSONResponse(content={"status": "success", "message": "Test webhook sent", "payload": test_payload}, status_code=200)

# @app.get("/")
# async def root():
#     """Root endpoint with basic info"""
#     return JSONResponse(content={
#         "message": "Simple Webhook Server",
#         "endpoints": {
#             "webhook": "/webhook (POST)",
#             "health": "/health (GET)"
#         }
#     }, status_code=200)

if __name__ == '__main__':
    print("Starting Simple Webhook Server...")
    print("Server will listen on http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info") 