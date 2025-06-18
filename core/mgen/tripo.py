import asyncio
import os
import requests
from dotenv import load_dotenv
import asyncio
import websockets
import json
import time
from typing import Optional, Union

load_dotenv()

API_KEY = os.getenv("TRIPPO_API_KEY")

def create_text_to_model_task(prompt: str) -> dict:
    """
    Create a text-to-model task using the Tripo API.
    
    Args:
        prompt (str): The text prompt to generate a 3D model from
        
    Returns:
        dict: The API response containing task information
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    url = "https://api.tripo3d.ai/v2/openapi/task"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "type": "text_to_model",
        "prompt": prompt
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

async def receive_one(tid):
  url = f"wss://api.tripo3d.ai/v2/openapi/task/watch/{tid}"
  headers = {
      "Authorization": f"Bearer {API_KEY}"
  }
  async with websockets.connect(url, additional_headers=headers) as websocket:
      while True:
          message = await websocket.recv()
          try:
              data = json.loads(message)
              status = data['data']['status']
              if status not in ['running', 'queued']:
                  break
          except json.JSONDecodeError:
              print("Received non-JSON message:", message)
              break
  return data

async def upload_file(file_input: Union[str, bytes], format: str):
    """
    Upload a file to Tripo API. Can accept either a file path or raw image content.
    
    Args:
        file_input (Union[str, bytes]): Either a file path (str) or raw image content (bytes)
        format (str): The format of the image ('webp', 'jpeg', or 'png')
        
    Returns:
        dict: The API response containing upload information
        
    Raises:
        ValueError: If the format is not one of the accepted types (webp, jpeg, png)
    """
    ACCEPTED_FORMATS = {'webp', 'jpeg', 'png'}
    format = format.lower()
    
    if format not in ACCEPTED_FORMATS:
        raise ValueError(f"Format must be one of {ACCEPTED_FORMATS}. Got: {format}")
    
    url = "https://api.tripo3d.ai/v2/openapi/upload/sts"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    if isinstance(file_input, str):
        # Handle file path
        with open(file_input, "rb") as f:
            print("file found:", file_input)
            files = {'file': (file_input, f, f'image/{format}')}
            response = requests.post(url, headers=headers, files=files)
    else:
        # Handle raw image content
        files = {'file': (f'image.{format}', file_input, f'image/{format}')}
        response = requests.post(url, headers=headers, files=files)
    
    return response.json()

async def generate_model(
        model_version: str,
        file: dict,
        file_type: str,
        model_seed: int,
        texture: bool,
        style: str,
        auto_size: bool = False,
        orientation: str = "default",
        quad: bool = False,
        type: str = "image_to_model",
    ):
    url = "https://api.tripo3d.ai/v2/openapi/task"

    data = {
        "type": type,
        "file": {
            "type": file_type,
            "file_token": file["data"]["image_token"]
        },
        # "model_version": model_version,
        # "model_seed": model_seed,
        # "texture": texture,
        # "auto_size": auto_size,
        # "style": style,
        # "orientation": orientation,
        # "quad": quad
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

async def get_model_output(task_id: str) -> Optional[dict]:
    result = asyncio.run(receive_one(task_id))

    if result['event'] == 'finalized':
        return None

    pbr_model_url = result['data']['result']['pbr_model']['url']
    rendered_image_url = result['data']['result']['rendered_image']['url']

    return {
        "pbr_model_url": pbr_model_url,
        "rendered_image_url": rendered_image_url,
    }

if __name__ == "__main__":
    # prompt = "a small cat"

    # upload the file
    # file_path = "images/parents_home.png"
    # format = "png"
    # success = asyncio.run(upload_file(file_path, format))
    # print(success)

    success = {'code': 0, 'data': {'image_token': '3f04687c-fc71-484c-b1fb-dfa2d158a3c5'}}

    # Generate the model
    # model_version = "v2.5-20250123"
    # file = success
    # file_type = "png"
    # model_seed = 42
    # texture = False
    # style = "default"
    # task = asyncio.run(generate_model(model_version, file, file_type, model_seed, texture, style))
    # print(task)

    # task = {'code': 0, 'data': {'task_id': 'a32d1cef-e70e-4b6c-9e0d-1a187c76dca3'}}
    # task = {'code': 0, 'data': {'task_id': '2ed8bda2-643c-41e2-88d3-3df19ef1f282'}}
    # task = {'code': 0, 'data': {'task_id': 'dbf86d89-7bc8-4da6-bfd9-54897767d356'}}

    # task_id = task["data"]["task_id"]
    # start = time.time()
    # while True:
    #     result = asyncio.run(receive_one(task_id))
    #     print(result["event"])
    #     if result['event'] == 'finalized':
    #         break
    #     time.sleep(1)

    # end = time.time()
    # print(f"Generated model in {end - start} seconds")

    # pbr_model_url = result['data']['result']['pbr_model']['url']
    # rendered_image_url = result['data']['result']['rendered_image']['url']

    # # print(rendered_image_url)
    # print(pbr_model_url)

