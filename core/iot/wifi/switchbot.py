import os
import json
import time
import hashlib
import hmac
import base64
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SWITCHBOT_TOKEN")
secret = os.getenv("SWITCHBOT_SECRET")
api_url = os.getenv("SWITCHBOT_API_URL")
model_no = "W4402000"

# Declare empty header dictionary
def generate_signed_header():
    apiHeader = {}

    nonce = uuid.uuid4()
    t = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(token, t, nonce)

    string_to_sign = bytes(string_to_sign, 'utf-8')
    _secret = bytes(secret, 'utf-8')

    sign = base64.b64encode(hmac.new(_secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

    #Build api header JSON
    apiHeader['Authorization']=token
    apiHeader['Content-Type']='application/json'
    # apiHeader['charset']='utf8'
    # apiHeader['t']=str(t)
    # apiHeader['sign']=str(sign, 'utf-8')
    # apiHeader['nonce']=str(nonce)

    return apiHeader

def get_device_list():
    url = f"{api_url}/v1.1/devices"
    headers = generate_signed_header()
    response = requests.get(url, headers=headers)
    return response.json()

def get_device_status(device_id):
    url = f"{api_url}/v1.1/devices/{device_id}/status"
    headers = generate_signed_header()
    response = requests.get(url, headers=headers)
    return response.json()

def send_command(device_id, command):
    url = f"{api_url}/v1.1/devices/{device_id}/commands"
    headers = generate_signed_header()
    data = {
        "command": command,
        "parameter": "default",
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def set_up_webhook(
        action: str = "setupWebhook", 
        wh_url: str = "http://localhost:5000", 
        device_list: str = "ALL"
    ):
    url = "https://api.switch-bot.com/v1.1/webhook/setupWebhook"
    headers = generate_signed_header()
    data = {
        "action": action,
        "url": wh_url,
        "deviceList": device_list
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def query_webhook_config(
        action: str = "queryDetails",
        wh_url: str = "http://localhost:5000"
    ):
    """Query current webhook configuration"""
    url = "https://api.switch-bot.com/v1.1/webhook/queryWebhook"
    headers = generate_signed_header()
    data = {
        "action": action,
        "urls": [wh_url]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def update_webhook_config(
        wh_url: str = "http://localhost:5000", 
        device_list: str = "ALL"
    ):
    """Update webhook configuration"""
    url = "https://api.switch-bot.com/v1.1/webhook/updateWebhook"
    headers = generate_signed_header()
    data = {
        "url": wh_url,
        "deviceList": device_list
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def delete_webhook(
        action: str = "deleteWebhook", 
        wh_url: str = "http://localhost:5000"
    ):
    """Delete webhook configuration"""
    url = "https://api.switch-bot.com/v1.1/webhook/deleteWebhook"
    headers = generate_signed_header()
    data = {
        "action": action,
        "url": wh_url
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def configure_webhook_with_ngrok():
    """
    Configure the webhook with a new URL using ngrok. Ngrok free tier
    creates a new URL every time the server is restarted, so this will help
    automate the update of the webhook URL.
    
    This function will:
    1. Delete the current webhook
    2. Set up a new webhook with the ngrok URL
    3. Query the webhook config
    4. Return the current webhook config
    """
    # Read the current webhook config from a file
    with open("webhook_config.json", "r") as f:
        current_config = json.load(f)
    inital_webhook_url = current_config['body'][0]['url']

    # Find the current ngrok URL
    headers = {
        "Authorization": f"Bearer {os.getenv('NGROK_API_KEY')}",
        "Ngrok-Version": "2"
    }
    response = requests.get("https://api.ngrok.com/tunnels", headers=headers)
    if response.status_code == 200:
        tunnels = response.json()
        for tunnel in tunnels.get("tunnels", []):
            if tunnel.get("proto") == "https":
                new_webhook_url = tunnel.get("public_url")
    
    # Delete the current webhook
    success = delete_webhook(wh_url=inital_webhook_url)
    if success['statusCode'] != 100:
        print(f"Failed to delete webhook from {inital_webhook_url}")
        # No early return since this can indicate that the webhook is already deleted
        # return False
    
    # # Set up webhook with ngrok URL
    success = set_up_webhook(wh_url=new_webhook_url)
    if success['statusCode'] != 100:
        print(f"Failed to set up webhook to {new_webhook_url}")
        return False
    
    # # Query webhook config
    current_config = query_webhook_config(wh_url=new_webhook_url)

    # Write the current webhook config to a file for reference
    with open("webhook_config.json", "w") as f:
        json.dump(
            current_config, 
            f,
            indent=2
        )
    return current_config
    

if __name__ == "__main__":
    # print(get_device_list())
    # configure_webhook_with_ngrok()
    device_id = "CE2A83C62F6C"
    print(get_device_status(device_id))

