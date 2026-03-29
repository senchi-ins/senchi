import json
from openai import OpenAI
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_improvements():
    """Load the predefined home improvements from the JSON file."""
    with open('experiments/2dto3d/improvements.txt', 'r') as f:
        data = json.load(f)
    return data['home_improvements']

def encode_image_to_base64(image_path):
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_house_image(image_path, client):
    """Analyze a house image using OpenAI's Vision API and return improvement recommendations."""
    improvements = load_improvements()
    
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

    # Encode the image
    base64_image = encode_image_to_base64(image_path)

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
    
    return response.choices[0].message.content

def main():
    """Main function to process an image and get recommendations."""
    # Process the test image
    image_path = "experiments/2dto3d/test.png"
    
    # Initialize OpenAI client
    client = OpenAI()
    
    try:
        recommendations_json = analyze_house_image(image_path, client)
        # Parse and pretty print the JSON
        recommendations = json.loads(recommendations_json)
        print("\nRecommended Improvements:")
        print(json.dumps(recommendations, indent=2))
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")

if __name__ == "__main__":
    main()
