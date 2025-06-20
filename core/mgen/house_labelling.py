import json
import os
from typing import Dict, List, Optional, Union, Tuple
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
    with open('mgen/improvement.json', 'r') as f:
        data = json.load(f)
    return data['home_improvements']

async def load_rubrics() -> List[Dict]:
    """
    Load the rubrics for scoring home improvements.
    
    Returns:
        List[Dict]: List of rubric dictionaries
    """
    with open('mgen/improvement_rubric.json', 'r') as f:
        data = json.load(f)
    return data['rubrics']

def calculate_house_score(scores: List[str]) -> float:
    """
    Calculate the final house score based on individual category scores.
    
    Args:
        scores (List[str]): List of scores ('low', 'medium', 'high')
        
    Returns:
        float: Final house score out of 100
    """
    score_values = {
        'high': 6.666,
        'medium': 4,
        'low': 1
    }
    
    total_score = sum(score_values[score] for score in scores)
    return round(total_score)

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

async def analyze_house_images(image_inputs: List[Union[str, bytes]], client: OpenAI) -> Optional[Dict]:
    """
    Analyze multiple views of a house using OpenAI's Vision API and return a comprehensive assessment.
    
    Args:
        image_inputs (List[Union[str, bytes]]): List of image paths or raw image content
        client (OpenAI): OpenAI client instance
        
    Returns:
        Optional[Dict]: JSON response containing scores, recommendations and final score, or None if failed
    """
    try:
        improvements = await load_improvements()
        rubrics = await load_rubrics()
        
        # Create list of improvements with full details
        improvements_text = "\n".join([
            f"Improvement {i+1}:\n" +
            f"- Title: {imp['title']}\n" +
            f"- Description: {imp['description']}\n" +
            f"- Location: {imp['location']}"
            for i, imp in enumerate(improvements)
        ])
        
        # Create scoring criteria list
        scoring_text = "\n".join([
            f"Category {i+1}: {rubric['title']}\n" +
            f"Location: {rubric['location']}\n" +
            f"Scoring Criteria:\n" +
            f"- Low: {rubric['rubric']['low'] if isinstance(rubric['rubric']['low'], str) else ', '.join(rubric['rubric']['low'])}\n" +
            f"- Medium: {rubric['rubric']['medium'] if isinstance(rubric['rubric']['medium'], str) else ', '.join(rubric['rubric']['medium'])}\n" +
            f"- High: {rubric['rubric']['high'] if isinstance(rubric['rubric']['high'], str) else ', '.join(rubric['rubric']['high'])}"
            for i, rubric in enumerate(rubrics)
        ])

        prompt = f"""You are a home safety and disaster preparedness expert. You will be provided with one or more views of a house. Using ALL provided views to make your assessment:

1. From this list of available improvements, understand what suggested improvements you are able to recommend.
{improvements_text}

2. Score each category as either 'low', 'medium', or 'high' based on the following criteria:

{scoring_text}

3. From this list of available improvements, identify the three most critical ones needed (those scored as 'low'):

{improvements_text}

4. For the three improvements that you identified as most critical, provide the x, y coordinate of where the improvement is located on the image.

Use all provided views of the house to make your assessment. If certain aspects aren't visible in any view, mention this in your explanations.

Format your response as a valid JSON string with this exact structure:
{{
    "category_scores": [
        {{
            "title": "Category title",
            "score": "low/medium/high"
        }},
        // for all 15 categories
    ],
    "recommendations": [
        {{
            "title": "Exact title from list",
            "description": "Exact description from list",
            "location": "Exact location from list",
            "explanation": "Your specific explanation based on all provided views",
            "x": "x coordinate of the improvement",
            "y": "y coordinate of the improvement"
        }},
        // for the three most critical improvements (scored as low)
    ],
    "final_score": "Final house score out of 100"
}}
The output format must be the JSON string as shown above. No other text or formatting.
"""

        try:
            # Encode all images
            image_contents = []
            for img_input in image_inputs:
                base64_image = await encode_image_to_base64(img_input)
                image_contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            # Construct message content with text and all images
            message_content = [{"type": "text", "text": prompt}] + image_contents

            # Call the OpenAI Vision API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                max_tokens=1500,
                response_format={ "type": "json_object" }
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Calculate the final house score
            scores = [item['score'].lower() for item in result['category_scores']]
            final_score = calculate_house_score(scores)
            
            # Add the final score to the result
            result['final_score'] = final_score
            
            # Save the result to a JSON file
            output_filename = 'house_analysis_result.json'
            with open(output_filename, 'w') as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing images: {str(e)}")
            return None
    except Exception as e:
        print(f"Error analyzing images: {str(e)}")
        return None

async def label_house(image_inputs: List[Union[str, bytes]]) -> Optional[Dict]:
    """
    Main function to process one or more views of a house and get a comprehensive assessment.
    
    Args:
        image_inputs (List[Union[str, bytes]]): List of image paths or image content
        
    Returns:
        Optional[Dict]: Dictionary containing category scores, recommendations, and final score
    """
    client = OpenAI()
    
    try:
        result = await analyze_house_images(image_inputs, client)
        return result
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return None