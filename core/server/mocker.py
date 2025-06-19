import requests

address = "383 Wettlaufer Terrace, Milton, ON, L9T 7N4"
# prod_api_url = "https://api.senchi.ca/api/v1/risk/upload-file"
dev_api_url_base = "http://localhost:8000/api/v1/risk"

health_check = dev_api_url_base + "/"
# response = requests.get(health_check)

# response = requests.post(
#     dev_api_url_base + "/upload-file",
#     params={"address": address, "heading": 120, "bucket": "senchi-gen-dev"}
# )

# response = {'code': 0, 'data': {'image_token': '6ae37d34-0462-41b8-8f4d-2bad3cc3e5f6'}}

# file = response
# file_type = "png"

# task = requests.post(
#     dev_api_url_base + "/generate-model",
#     json={
#         "file": file, 
#         "file_type": file_type, 
#         "model_type": "image_to_model"
#     }
# )

# print(task.json())

task = {'code': 0, 'data': {'task_id': '2b434ee4-cc3d-4f91-a144-cf2974617ac6'}}

task_id = task["data"]["task_id"]

response = requests.get(
    dev_api_url_base + "/get-model-output",
    params={"task_id": task_id}
)

print(response.json())

