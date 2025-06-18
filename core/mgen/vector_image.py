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

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

async def prepare_image(file_input: Union[str, bytes], format: str = "png") -> BytesIO:
    """
    Prepare an image for the OpenAI API. Can accept either a file path or raw image content.
    
    Args:
        file_input (Union[str, bytes]): Either a file path (str) or raw image content (bytes)
        format (str): The format of the image (default: 'png')
        
    Returns:
        BytesIO: Image buffer ready for API submission
        
    Raises:
        ValueError: If the format is not supported or file cannot be processed
    """
    try:
        if isinstance(file_input, str):
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
        img_buffer.seek(0)
        
        return img_buffer
    
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")

async def generate_vector_image(
    image_buffer: BytesIO,
    style: str = "isometric",
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

    # Style-specific prompts
    style_prompts = {
        "isometric": """Turn this image into an isometric vector illustration with clean outlines, 
        simplified shapes, soft shadows, and muted colors; flat 3D perspective similar to architectural 
        diagrams or infographics; minimalistic, cartoon-like, and neatly stylized. Remove all other 
        noise from the photo including neighbouring houses, snow, lamp posts, and cars. Keep only the 
        main house and the surrounding trees, shrubs, and grass."""
    }

    # Get the appropriate prompt
    prompt = style_prompts.get(style, style_prompts["isometric"])

    try:
        # Generate the vector image using gpt-image-1
        response = await client.images.edit(
            model="gpt-image-1",
            image=image_buffer,
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )

        if response and response.data:
            return {"url": response.data[0].url}
        else:
            raise Exception("No output received from the API")

    except Exception as e:
        raise Exception(f"Failed to generate vector image: {str(e)}")

async def get_vector_image(url: str, output_path: Optional[str] = None) -> str:
    """
    Download and save the generated vector image.
    
    Args:
        url (str): URL of the generated image
        output_path (Optional[str]): Path where to save the image
        
    Returns:
        str: Path to the saved image
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        if output_path is None:
            output_path = f"output_vector_{int(time.time())}.png"

        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path

    except Exception as e:
        raise Exception(f"Failed to download vector image: {str(e)}")

async def process_vector_image(
    input_path: str,
    output_path: Optional[str] = None,
    style: str = "isometric",
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
        # Prepare the image
        image_buffer = await prepare_image(input_path)
        
        # Generate the vector image
        result = await generate_vector_image(image_buffer, style=style)
        
        # Download and save the result
        final_path = await get_vector_image(result["url"], output_path)
        
        return final_path

    except Exception as e:
        raise Exception(f"Failed to process vector image: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_image = "path/to/input.png"
    output_image = "path/to/output.png"
    
    try:
        result_path = asyncio.run(process_vector_image(input_image, output_image))
        print(f"Vector image saved to: {result_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
