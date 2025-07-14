import json
import os
from typing import Dict, List, Optional, Union, Tuple
from openai import OpenAI
import base64
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

async def load_improvements() -> List[Dict[str, str]]:
    """
    Load the predefined home improvements from the JSON file.
    
    Returns:
        List[Dict[str, str]]: List of home improvement dictionaries
    """
    improvements_path = os.path.join(script_dir, 'improvement.json')
    with open(improvements_path, 'r') as f:
        data = json.load(f)
    return data['home_improvements']

async def load_rubrics() -> List[Dict]:
    """
    Load the rubrics for scoring home improvements.
    
    Returns:
        List[Dict]: List of rubric dictionaries
    """
    rubrics_path = os.path.join(script_dir, 'improvement_rubric.json')
    with open(rubrics_path, 'r') as f:
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

        prompt = f"""You are a home-safety and disaster-preparedness expert.

You will be given one or more exterior views of a house.  
Use *all* views for your assessment.

COORDINATE SYSTEM
• You will output (x, y) pixel coordinates on the **front-facing STREET-VIEW image only**.  
• Origin (0, 0) is the **top-left corner**.  
• The image width is <IMG_WIDTH> px and height is <IMG_HEIGHT> px.  
• Coordinates must be integers (round or floor as needed).

TASKS
1. Use all views to identify potential improvements from this list:  
{improvements_text}

2. Score every category as “low”, “medium”, or “high” using:  
{scoring_text}

3. Choose the **three most critical improvements** (those whose category you scored “low”).

4. For each of those three, output a pixel location that marks **where the improvement should actually be made** on the front image.

SPACING RULE
To avoid overlap, the **Euclidean distance between any two of your (x, y) coordinates must be ≥ 100 pixels**.  
If two recommended fixes would naturally fall closer than that, adjust one point slightly (while keeping it on the correct feature) so the rule holds.

OUTPUT
Return a single valid JSON string in exactly this structure - nothing else:

{{
  "category_scores": [
    {{
      "title": "Category title",
      "score": "low|medium|high"
    }}
    // ...15 total
  ],
  "recommendations": [
    {{
      "title": "Exact title from list",
      "description": "Exact description from list",
      "location": "Exact location from list",
      "explanation": "Specific reasoning using ALL views",
      "x":  <integer x>,
      "y":  <integer y>
    }}
    // ...exactly 3 objects
  ],
  "final_score": "Score out of 100"
}}

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