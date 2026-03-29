import os
import json
import requests
import certifi
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
MESHY_API_KEY = os.getenv('MESHY_API')
MESHY_API_URL = 'https://api.meshy.ai/openapi/v1/image-to-3d'

def read_base64_from_file(file_path):
    """Read base64 data from a file."""
    with open(file_path, 'r') as f:
        return f.read().strip()

def create_3d_model(base64_data):
    """Create a 3D model from base64 image data using Meshy API."""
    headers = {
        'Authorization': f'Bearer {MESHY_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Ensure the base64 data has the correct prefix
    if not base64_data.startswith('data:image/'):
        base64_data = 'data:image/png;base64,' + base64_data
    
    payload = {
        'image_url': base64_data,
        'enable_pbr': True,
        'should_remesh': True,
        'should_texture': True,
        'ai_model': 'meshy-5',  # Using the latest model
        'topology': 'quad',      # Using quad topology for better quality
    }
    
    try:
        # Create the task with SSL verification using certifi
        response = requests.post(
            MESHY_API_URL,
            headers=headers,
            json=payload,
            verify=certifi.where()
        )
        response.raise_for_status()
        task_id = response.json()['result']
        print(f"Task created with ID: {task_id}")
        
        # Poll for task completion
        while True:
            status_response = requests.get(
                f"{MESHY_API_URL}/{task_id}",
                headers=headers,
                verify=certifi.where()
            )
            status_response.raise_for_status()
            task_status = status_response.json()
            
            if task_status['status'] == 'SUCCEEDED':
                print("Task completed successfully!")
                return task_status
            elif task_status['status'] == 'FAILED':
                raise Exception(f"Task failed: {task_status['task_error']['message']}")
            elif task_status['status'] in ['PENDING', 'IN_PROGRESS']:
                print(f"Progress: {task_status['progress']}%")
                time.sleep(5)  # Wait 5 seconds before checking again
            else:
                raise Exception(f"Unknown status: {task_status['status']}")
    
    except requests.exceptions.SSLError as e:
        print("SSL Error encountered. This might be due to outdated certificates.")
        print("Try running: pip install --upgrade certifi")
        print(f"Error details: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        raise

def download_model_files(task_status, output_dir='output'):
    """Download all model files and textures."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Download model files
    for format_name, url in task_status['model_urls'].items():
        response = requests.get(url, verify=certifi.where())
        with open(os.path.join(output_dir, f'model.{format_name}'), 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {format_name} model")
    
    # Download textures
    for i, texture_set in enumerate(task_status['texture_urls']):
        for texture_type, url in texture_set.items():
            response = requests.get(url, verify=certifi.where())
            with open(os.path.join(output_dir, f'texture_{i}_{texture_type}.png'), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {texture_type} texture")

def main():
    # Read the base64 data from test.txt
    base64_data = read_base64_from_file('experiments/2dto3d/test.txt')
    
    # Create the 3D model
    task_status = create_3d_model(base64_data)
    
    # Download the resulting files
    download_model_files(task_status)
    
    print("Process completed successfully!")

if __name__ == "__main__":
    main()
