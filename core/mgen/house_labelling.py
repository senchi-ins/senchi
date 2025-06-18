import json
import os
from typing import Dict, List, Optional, Union
from openai import OpenAI
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

async def load_improvements() -> List[Dict[str, str]]:
    """
    Load the predefined home improvements from the JSON file.
    
    Returns:
        List[Dict[str, str]]: List of home improvement dictionaries
    """
    with open('core/mgen/improvement.txt', 'r') as f:
        data = json.load(f)
    return data['home_improvements']

async def encode_image_to_base64(image_input: Union[str, bytes]) -> str:
    """
    Convert an image to base64 string. Can accept either a file path or raw image content.
    
    Args:
        image_input (Union[str, bytes]): Either a file path (str) or raw image content (bytes)
        
    Returns:
        str: Base64 encoded image string
    """
    if isinstance(image_input, str):
        # Handle file path
        with open(image_input, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    else:
        # Handle raw image content
        return base64.b64encode(image_input).decode('utf-8')

async def analyze_house_image(image_input: Union[str, bytes], client: OpenAI) -> Optional[Dict]:
    """
    Analyze a house image using OpenAI's Vision API and return improvement recommendations.
    
    Args:
        image_input (Union[str, bytes]): Either a file path (str) or raw image content (bytes)
        client (OpenAI): OpenAI client instance
        
    Returns:
        Optional[Dict]: JSON response containing recommendations or None if failed
        
    Raises:
        Exception: If analysis fails
    """
    improvements = await load_improvements()
    
    # Create a comprehensive list of improvements for the prompt
    improvements_text = "\n".join([
        f"- {imp['title']}: {imp['description']} (Location: {imp['location']})"
        for imp in improvements
    ])

    # Craft the prompt for the vision model
    prompt = f"""You are a home safety and disaster preparedness expert. Analyze this house image and recommend exactly 3 specific improvements from the following list that would best protect this house from natural disasters and catastrophic events. Focus on the most visible and critical areas that need attention.

Available improvements:
{improvements_text}

For each recommendation, select from the exact improvements listed above and provide:
1. The exact title as listed
2. The exact description as listed
3. The exact location as listed
4. A brief explanation of why this improvement is needed based on what you see in the image

Format your response as a valid JSON string with this exact structure:
{{
    "recommendations": [
        {{
            "title": "Exact title from list",
            "description": "Exact description from list",
            "location": "Exact location from list",
            "explanation": "Your specific explanation based on the image"
        }},
        // two more similar objects
    ]
}}"""

    try:
        # Encode the image
        base64_image = await encode_image_to_base64(image_input)

        # Call the OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return None

async def label_house(image_input: Union[str, bytes]):
    """Main function to process an image and get recommendations."""
    client = OpenAI()
    
    try:
        recommendations = await analyze_house_image(image_input, client)
        return recommendations
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return None