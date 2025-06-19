import asyncio
import os
import requests
from dotenv import load_dotenv
import asyncio
import websockets
import json
import time

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

async def upload_file(file_path: str, format: str):
    url = "https://api.tripo3d.ai/v2/openapi/upload/sts"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    with open(file_path, "rb") as f:
        print("file found:", file_path)
        files = {'file': (file_path, f, 'image/png')}
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

if __name__ == "__main__":
    # prompt = "a small cat"

    # upload the file
    file_path = "https://senchi-gen-dev.s3.amazonaws.com/5e2fa30ef3068eca8d202780f0413519549ce6ac517359c3147fcbb780ee2a1c_vector.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5FG6V3P65DCFWZNC%2F20250619%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250619T011813Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=73e7c7e6a2a2c6f3b28eb0a56872158e079813bdb6b970d2151b6c61599cbded"
    format = "png"
    success = asyncio.run(upload_file(file_path, format))
    print(success)

    # success = {'code': 0, 'data': {'image_token': '3f04687c-fc71-484c-b1fb-dfa2d158a3c5'}}

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

