import requests
from dotenv import load_dotenv

load_dotenv()

address = "383 Wettlaufer Terrace, Milton, ON, L9T 7N4"
# prod_api_url = "https://api.senchi.ca/api/v1/risk/upload-file"
# dev_api_url_base = "http://localhost:8000/api/v1/risk"
# dev_api_url_base = "http://localhost:8000/api/v1/labelling"
# prod_api_url_base = "https://api.senchi.ca/api/v1/labelling"
dev_api_url_base = "http://localhost:8000/api/v1"

# health_check = dev_api_url_base + "/"
# response = requests.get(health_check)

# response = requests.post(
#     dev_api_url_base + "/upload-file",
#     params={"address": address, "heading": 120, "bucket": "senchi-gen-dev"}
# )

# print(response.json())

# response = {'code': 0, 'data': {'image_token': '6ae37d34-0462-41b8-8f4d-2bad3cc3e5f6'}}
# response = {'code': 0, 'data': {'image_token': '6edeaff7-2212-4a86-9b00-065ed47210a2'}}

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

# task = {'code': 0, 'data': {'task_id': '2b434ee4-cc3d-4f91-a144-cf2974617ac6'}}
# task = {'code': 0, 'data': {'task_id': '3fcf4419-5b83-48e0-ba32-7141c2ccc37a'}}

# task_id = task["data"]["task_id"]

# response = requests.get(
#     dev_api_url_base + "/get-model-output",
#     params={"task_id": task_id}
# )

# print(response.json())

# response = requests.post(
#     prod_api_url_base + "/analyze-house",
#     params={"address": address, "heading": 120}
# )

# print(response.json())

# GLB url
url = "https://tripo-data.rg1.data.tripo3d.com/tcli_452312b4252d418cbd41cff1e5c98d35/20250622/3fcf4419-5b83-48e0-ba32-7141c2ccc37a/tripo_pbr_model_3fcf4419-5b83-48e0-ba32-7141c2ccc37a.glb?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly90cmlwby1kYXRhLnJnMS5kYXRhLnRyaXBvM2QuY29tL3RjbGlfNDUyMzEyYjQyNTJkNDE4Y2JkNDFjZmYxZTVjOThkMzUvMjAyNTA2MjIvM2ZjZjQ0MTktNWI4My00OGUwLWJhMzItNzE0MWMyY2NjMzdhL3RyaXBvX3Bicl9tb2RlbF8zZmNmNDQxOS01YjgzLTQ4ZTAtYmEzMi03MTQxYzJjY2MzN2EuZ2xiIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzUwNjM2ODAwfX19XX0_&Signature=aiAMnltES1ah07EZN~z-E8GHXQvAEujhI9IuKoG4ABk1n4qVhpLmSEX1Xqu9715KfE0h9UTd0RKHWT6S467YMC6CZnr6KfYx5xgafBPk05ZJ0Q6WtAazVkRibi~eh5Cy3kt-BRn90n5OvntViEjumhozVm7WlAQT84QE1XzT3rZCrHKjjijUAFSdR6xsBZGRRlY82fJgM7Rhk9EIC~k-oz9Deg8CeQP5duglBbdbD37ceCpKhjUGGoh1j04jmfnbNh7FX461kv1GkHDACWeB6i4pEcIQAYNwEcIQny46bqd1-DEm-eyVXqxQbsdhtixjZFV2s79PCV-H97qsNrLz4A__&Key-Pair-Id=K1676C64NMVM2J"

response = requests.get(
    dev_api_url_base + "/proxy",
    params={"url": url}
)

print(response.text)