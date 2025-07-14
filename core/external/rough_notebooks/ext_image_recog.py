import os
import json
from typing import List, Dict, Union, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ImageAnalyzer:
    def __init__(self):
        self.questions_map = self._load_questions()
        self.duplicate_questions = self._identify_duplicate_questions()

    def _normalize_question(self, question: str) -> str:
        """Normalize question text to identify similar questions."""
        # Remove punctuation, convert to lowercase, and normalize whitespace
        return " ".join(question.lower().replace("?", "").split())

    def _identify_duplicate_questions(self) -> Dict[str, List[str]]:
        """Identify questions that are duplicates or very similar across assessment types."""
        normalized_map = {}
        for question in self.questions_map:
            norm_q = self._normalize_question(question)
            if norm_q not in normalized_map:
                normalized_map[norm_q] = []
            normalized_map[norm_q].append(question)
        
        # Return only groups that have duplicates
        return {key: questions for key, questions in normalized_map.items() 
                if len(questions) > 1}

    def _load_questions(self) -> Dict[str, Dict[str, Union[str, Dict[str, int]]]]:
        """Load and combine questions from both JSON files."""
        questions_map = {}
        
        # Load flood questions
        with open("core/ext_analysis/flood_qeustions.json", "r") as f:
            flood_data = json.load(f)
            for q in flood_data["questions"]:
                key = q["question"]
                if key in questions_map:
                    # If question exists, merge the types and keep highest rubric scores
                    questions_map[key]["types"].append("flood")
                    for answer, score in q["rubric"].items():
                        if answer in questions_map[key]["rubric"]:
                            questions_map[key]["rubric"][answer] = max(
                                questions_map[key]["rubric"][answer],
                                score
                            )
                else:
                    questions_map[key] = {
                        "types": ["flood"],
                        "rubric": q["rubric"]
                    }
        
        # Load winter questions
        with open("core/ext_analysis/severe_winter_questions.json", "r") as f:
            winter_data = json.load(f)
            for q in winter_data["questions"]:
                key = q["question"]
                if key in questions_map:
                    # If question exists, merge the types and keep highest rubric scores
                    questions_map[key]["types"].append("winter")
                    for answer, score in q["rubric"].items():
                        if answer in questions_map[key]["rubric"]:
                            questions_map[key]["rubric"][answer] = max(
                                questions_map[key]["rubric"][answer],
                                score
                            )
                else:
                    questions_map[key] = {
                        "types": ["winter"],
                        "rubric": q["rubric"]
                    }
        
        return questions_map

    def should_request_photos(self, question: str, user_answer: str) -> bool:
        """
        Determine if photos should be requested based on the question and user's answer.
        
        Args:
            question: The question being asked
            user_answer: The user's response ('Yes' or 'No')
            
        Returns:
            bool: True if photos should be requested, False otherwise
        """
        # Logic for when to request photos based on question type and answer
        photo_validation_rules = {
            "Does your roof have any shingles that are missing, cracked, curled or otherwise damaged?": {
                "Yes": True,  # Verify extent of damage
                "No": True    # Verify if truly undamaged
            },
            "Is all ice and snow cleared from drains, gutters, and downspouts?": {
                "Yes": True,  # Verify if truly clear
                "No": False   # No need to verify if user admits to blockage
            },
            "Are your eavesdrops, drains, gutters, and roof free of debris?": {
                "Yes": True,  # Verify if truly clean
                "No": False   # No need to verify if user admits to debris
            },
            "Are any tree limbs or branches hanging over your home?": {
                "Yes": True,  # Verify extent of overhang
                "No": True    # Verify if truly clear
            },
            "Are there any tree limbs or branches that are hanging over your home?": {
                "Yes": True,  # Verify extent of overhang
                "No": True    # Verify if truly clear
            },
            "Are your ridge, soffit, gable and/or attic vents properly sealed and free of debris?": {
                "Yes": True,  # Verify condition and cleanliness
                "No": False   # No need to verify if user admits to issues
            },
            "Are your gutters made of steel or another type of metal?": {
                "Yes": True,  # Verify material type
                "No": True    # Verify material type
            },
            "Are your gutters and downspouts securely attached to the house and pointed away from the foundation?": {
                "Yes": True,  # Verify proper installation
                "No": False   # No need to verify if user admits to issues
            }
        }
        
        # Get validation rule for this question
        question_rules = photo_validation_rules.get(question)
        if question_rules is None:
            return False  # If question isn't in our rules, no photos needed
        return question_rules.get(user_answer, False)

    def get_photo_instructions(self, question: str) -> List[str]:
        """
        Get specific instructions for what photos to take based on the question.
        
        Args:
            question: The question being validated
            
        Returns:
            List of specific photo instructions
        """
        photo_instructions = {
            "Does your roof have any shingles that are missing, cracked, curled or otherwise damaged?": [
                "Take photos of each roof section",
                "Take close-up photos of any areas that look damaged",
                "Take photos from multiple angles if possible",
                "If safe, take photos from a ladder for better detail"
            ],
            "Is all ice and snow cleared from drains, gutters, and downspouts?": [
                "Take photos of each gutter and downspout",
                "Take close-up photos of drain openings",
                "Take photos showing any areas where ice or snow might accumulate",
                "If possible, take photos showing water flow paths"
            ],
            "Are your eavesdrops, drains, gutters, and roof free of debris?": [
                "Take a clear photo of each gutter section",
                "Take close-up photos of downspouts and drain areas",
                "Take a photo of the roof edges where gutters connect",
                "If possible, take a photo showing inside the gutters"
            ],
            "Are any tree limbs or branches hanging over your home?": [
                "Take photos of each side of the house where trees are present",
                "Take wide-angle shots showing full height of trees near the house",
                "Take photos from different angles to show branch overhang"
            ],
            "Are there any tree limbs or branches that are hanging over your home?": [
                "Take photos of each side of the house where trees are present",
                "Take wide-angle shots showing full height of trees near the house",
                "Take photos from different angles to show branch overhang"
            ],
            "Are your ridge, soffit, gable and/or attic vents properly sealed and free of debris?": [
                "Take close-up photos of each vent",
                "Take photos showing the seals around vents",
                "Take photos showing any potential debris accumulation",
                "If possible, take photos from multiple angles"
            ],
            "Are your gutters made of steel or another type of metal?": [
                "Take close-up photos of gutter material",
                "Take photos showing any manufacturer markings if visible",
                "Take photos of different sections of guttering",
                "If possible, take photos showing both interior and exterior of gutters"
            ],
            "Are your gutters and downspouts securely attached to the house and pointed away from the foundation?": [
                "Take photos of each gutter attachment point",
                "Take photos showing where downspouts connect to gutters",
                "Take photos showing where downspouts direct water at ground level",
                "Take photos of any extensions or splash blocks"
            ]
        }
        
        return photo_instructions.get(question, ["Take clear photos of the relevant areas"])

    def _get_analysis_prompt(self, question: str) -> str:
        """
        Generate a specific prompt based on the question type.
        Returns a detailed prompt with specific criteria for analysis.
        """
        prompts = {
            "Does your roof have any shingles that are missing, cracked, curled or otherwise damaged?": """
                Analyze this image of the roof.
                Look specifically for:
                - Missing shingles
                - Cracked or broken shingles
                - Curled or warped shingles
                - Any visible damage to roof surface
                
                Respond ONLY with:
                'Yes' - if damage is present
                'No' - if no damage is visible
                'Partially' - if minor wear is visible
                'Unclear' - if the image is not clear enough to determine
            """,
            
            "Is all ice and snow cleared from drains, gutters, and downspouts?": """
                Analyze this image of drains, gutters, and downspouts.
                Look specifically for:
                - Presence of ice or snow buildup
                - Blockages in drainage paths
                - Clear flow paths for water
                - Any ice dams or accumulation
                
                Respond ONLY with:
                'Yes' - if completely clear of ice and snow
                'No' - if significant ice or snow is present
                'Partially' - if minor accumulation exists
                'Unclear' - if the image is not clear enough to determine
            """,
            
            "Are your eavesdrops, drains, gutters, and roof free of debris?": """
                Analyze this image of eavesdrops, drains, gutters, or roof.
                Look specifically for:
                - Leaves, twigs, or other organic debris
                - Built-up sediment or dirt
                - Any blockages in gutters or drains
                - Clear flowing paths for water
                
                Respond ONLY with:
                'Yes' - if completely clear of debris
                'No' - if significant debris is present
                'Partially' - if minor debris is present
                'Unclear' - if the image is not clear enough to determine
            """,
            
            "Are any tree limbs or branches hanging over your home?": """
                Analyze this image of the house and surrounding trees.
                Look specifically for:
                - Tree branches extending over the roof
                - Proximity of trees to the house
                - Overhanging limbs near the structure
                
                Respond ONLY with:
                'Yes' - if branches are hanging over the home
                'No' - if no branches overhang the home
                'Partially' - if branches are close but not directly over
                'Unclear' - if the image is not clear enough to determine
            """,
            
            "Are your ridge, soffit, gable and/or attic vents properly sealed and free of debris?": """
                Analyze this image of vents.
                Look specifically for:
                - Proper sealing around vent edges
                - Presence of debris in or around vents
                - Damage to vent covers or screens
                - Signs of water infiltration
                
                Respond ONLY with:
                'Yes' - if properly sealed and clear
                'No' - if unsealed or blocked
                'Partially' - if minor issues present
                'Unclear' - if the image is not clear enough to determine
            """,
            
            "Are your gutters made of steel or another type of metal?": """
                Analyze this image of gutters.
                Look specifically for:
                - Material appearance and texture
                - Metallic sheen or characteristics
                - Any visible manufacturer markings
                - Signs of material type (seams, joints, etc.)
                
                Respond ONLY with:
                'Yes' - if clearly metal gutters
                'No' - if clearly non-metal material
                'Partially' - if mixed materials or uncertain
                'Unclear' - if the image is not clear enough to determine
            """,
            
            "Are your gutters and downspouts securely attached to the house and pointed away from the foundation?": """
                Analyze this image of gutters and downspouts.
                Look specifically for:
                - Gutter attachment to fascia
                - Downspout connection points
                - Downspout direction at ground level
                - Distance water is directed from foundation
                
                Respond ONLY with:
                'Yes' - if properly attached and directed
                'No' - if loose or improperly directed
                'Partially' - if some issues present but mostly functional
                'Unclear' - if the image is not clear enough to determine
            """
        }
        
        # Return specific prompt if available, otherwise return generic prompt
        return prompts.get(
            question,
            f"{question} Please analyze the image and respond with ONLY 'Yes', 'No', or 'Partially'. If the image is unclear or you cannot determine, respond with 'Unclear'."
        ).strip()

    def analyze_images(self, question: str, image_paths: List[str]) -> Dict:
        """
        Analyze a series of images related to a specific question.
        
        Args:
            question: The question being validated
            image_paths: List of paths to images to analyze
        
        Returns:
            Dict containing analysis results
        """
        if question not in self.questions_map:
            # Check if it's a known duplicate with different wording
            normalized_q = self._normalize_question(question)
            found = False
            for norm_key, questions in self.duplicate_questions.items():
                if normalized_q == norm_key:
                    question = questions[0]  # Use the first variant as canonical
                    found = True
                    break
            if not found:
                raise ValueError(f"Question not found in question bank: {question}")

        # Get the specific prompt for this question
        analysis_prompt = self._get_analysis_prompt(question)

        results = []
        for image_path in image_paths:
            try:
                with open(image_path, "rb") as image_file:
                    # Create message for vision API
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": analysis_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_file.read()}"
                                    }
                                }
                            ]
                        }
                    ]

                    # Make API call
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=100
                    )

                    # Extract response
                    analysis = response.choices[0].message.content.strip()
                    results.append({
                        "image_path": image_path,
                        "analysis": analysis
                    })

            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "error": str(e)
                })

        # Aggregate results
        final_result = self._aggregate_results(results)
        return {
            "question": question,
            "types": self.questions_map[question]["types"],
            "individual_results": results,
            "final_assessment": final_result
        }

    def _aggregate_results(self, results: List[Dict]) -> str:
        """
        Aggregate multiple image results into a final assessment.
        
        Logic:
        - If any image is 'No', final result is 'No'
        - If all images are 'Yes', final result is 'Yes'
        - If mix of 'Yes' and 'Partially', final result is 'Partially'
        - If any 'Unclear' and no 'No', final result is 'Unclear'
        """
        analyses = [r.get("analysis", "Unclear") for r in results if "error" not in r]
        
        if not analyses:
            return "Error"
        if "No" in analyses:
            return "No"
        if all(a == "Yes" for a in analyses):
            return "Yes"
        if "Unclear" in analyses:
            return "Unclear"
        return "Partially"

# Example usage:
if __name__ == "__main__":
    analyzer = ImageAnalyzer()
    
    # Example of checking if photos are needed
    question = "Are your eavesdrops, drains, gutters, and roof free of debris?"
    user_answer = "Yes"
    
    if analyzer.should_request_photos(question, user_answer):
        print(f"Please provide photos. Here are the photo instructions:")
        for instruction in analyzer.get_photo_instructions(question):
            print(f"- {instruction}")
        
        # Example analysis (once photos are provided)
        images = ["path/to/image1.jpg", "path/to/image2.jpg"]
        try:
            results = analyzer.analyze_images(question, images)
            print(json.dumps(results, indent=2))
        except Exception as e:
            print(f"Error during analysis: {e}")
    else:
        print("No photos needed for this response.")
