import asyncio
import os
import requests
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image
from openai import AsyncOpenAI
from typing import Optional, Union
import time

from mgen.prompts import openai_image_to_model_prompt

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

async def prepare_image(file_input: Union[str, bytes], format: str = "png") -> BytesIO:
    """
    Prepare an image for the OpenAI API. Can accept either a file path, URL, or raw image content.
    
    Args:
        file_input (Union[str, bytes]): Either a file path (str), URL (str), or raw image content (bytes)
        format (str): The format of the image (default: 'png')
        
    Returns:
        BytesIO: Image buffer ready for API submission
        
    Raises:
        ValueError: If the format is not supported or file cannot be processed
    """
    try:
        if isinstance(file_input, str):
            if file_input.startswith(('http://', 'https://')):
                # Handle URL
                response = requests.get(file_input)
                response.raise_for_status()  # Raise an exception for bad status codes
                img = Image.open(BytesIO(response.content))
            else:
                # Handle file path
                img = Image.open(file_input)
        else:
            # Handle raw image content
            img = Image.open(BytesIO(file_input))

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize image to fit requirements (1024x1024)
        img = img.resize((1024, 1024))
        
        # Prepare the image
        img_buffer = BytesIO()
        img.save(img_buffer, format=format)
        img_buffer.seek(0)  # Reset buffer position to start
        
        return img_buffer
    
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch image from URL: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")

async def generate_vector_image(
    image_buffer: BytesIO,
    prompt: str = openai_image_to_model_prompt,
) -> dict:
    """
    Generate a vector-style image using the OpenAI gpt-image-1 API.
    
    Args:
        image_buffer (BytesIO): Prepared image buffer
        style (str): Style of vector transformation (default: 'isometric')
        
    Returns:
        dict: The API response containing the generated image URL
    """
    if not API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    try:
        # Generate the vector image using gpt-image-1
        response = await client.images.edit(
            model="gpt-image-1",
            image=("image.png", image_buffer, "image/png"),
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

        if response and response.data:
            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            return image_bytes
        else:
            raise Exception("No output received from the API")

    except Exception as e:
        raise Exception(f"Failed to generate vector image: {str(e)}")


async def process_vector_image(
    input_path: str,
    output_path: Optional[str] = None,
    prompt: str = openai_image_to_model_prompt,
) -> str:
    """
    Complete pipeline to process an image into a vector illustration using OpenAI's DALL-E.
    
    Args:
        input_path (str): Path to the input image
        output_path (Optional[str]): Path where to save the output image
        style (str): Style of vector transformation
        
    Returns:
        str: Path to the processed image
    """
    try:
        image_buffer = await prepare_image(input_path)

        result = await generate_vector_image(image_buffer, prompt=prompt)

        return result
    
    except Exception as e:
        raise Exception(f"Failed to process vector image: {str(e)}")

if __name__ == "__main__":

    input_image = "https://senchi-gen-dev.s3.amazonaws.com/383%20Wettlaufer%20Terrace%2C%20Milton%2C%20ON%2C%20L9T%207N4_120.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5FG6V3P65DCFWZNC%2F20250618%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250618T234521Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=1b0467cccd7d9e22701ba6dd67461bb0e52eb123816fdb0b5d623e8e87df9be7"
    output_image = "images/testing.png"
    
    import time
    start_time = time.time()
    try:
        result_path = asyncio.run(process_vector_image(input_image, output_image))
        print(f"Vector image saved to: {result_path}")
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
    except Exception as e:
        print(f"Error: {str(e)}")
