"""
Module for handling photo capture and storage for risk assessment questions.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
from openai import OpenAI
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

class RiskPhotoManager:
    def __init__(self, bucket_name: str = "senchi-risk-photos"):
        """
        Initialize RiskPhotoManager with AWS S3 configuration.
        
        Args:
            bucket_name: Name of the S3 bucket to store photos
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        
    def _generate_photo_key(self, question_id: str, user_id: str) -> str:
        """Generate a unique S3 key for the photo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{user_id}/risk_photos/{question_id}/{timestamp}.jpg"
    
    def _generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for an S3 object."""
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expires_in
        )
        
    def upload_photo(self, photo_data: bytes, question_id: str, user_id: str) -> Optional[str]:
        """
        Upload a photo to S3 and return its URL.
        
        Args:
            photo_data: Raw photo data in bytes
            question_id: Identifier for the risk question
            user_id: Identifier for the user
            
        Returns:
            Optional[str]: URL of the uploaded photo if successful, None otherwise
        """
        try:
            # Generate unique key for the photo
            photo_key = self._generate_photo_key(question_id, user_id)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=photo_key,
                Body=photo_data,
                ContentType='image/jpeg'
            )
            
            # Generate a presigned URL that expires in 1 hour
            return self._generate_presigned_url(photo_key)
            
        except ClientError as e:
            print(f"Error uploading photo: {str(e)}")
            return None
            
    def get_photos_for_question(self, question_id: str, user_id: str) -> List[str]:
        """
        Get all photos associated with a specific question for a user.
        
        Args:
            question_id: Identifier for the risk question
            user_id: Identifier for the user
            
        Returns:
            List[str]: List of presigned URLs for the photos
        """
        try:
            # List objects with the prefix for this question
            prefix = f"{user_id}/risk_photos/{question_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            urls = []
            if 'Contents' in response:
                # Generate all URLs at once to avoid repeated method calls
                urls = [self._generate_presigned_url(obj['Key']) for obj in response['Contents']]
                    
            return urls
        except ClientError as e:
            print(f"Error retrieving photos: {str(e)}")
            return []
            
    def delete_photo(self, photo_url: str) -> bool:
        """
        Delete a photo from S3.
        
        Args:
            photo_url: URL of the photo to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Extract the key from the URL
            parsed_url = urlparse(photo_url)
            key = parsed_url.path.lstrip('/')
            
            # Delete the object
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            return True
        except ClientError as e:
            print(f"Error deleting photo: {str(e)}")
            return False

class RiskPhotoValidator:
    def __init__(self):
        """Initialize the validator with OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def _requires_photo_validation(self, user_answer: str, rubric: Dict[str, int]) -> bool:
        """
        Determine if photo validation is required based on the user's answer and rubric.
        
        Args:
            user_answer: The user's answer to the question
            rubric: The scoring rubric for the question (e.g. {"Yes": 1, "No": 0})
            
        Returns:
            bool: True if photo validation is required, False if not
        """
        # If the answer admits to a risk (score 0), no photo validation needed
        if user_answer in rubric and rubric[user_answer] == 0:
            return False
        return True
    
    def _create_error_response(self, error_message: str, verified: bool = False, 
                             matches_answer: bool = False, confidence: float = 0.0,
                             correct_answer: Optional[str] = None, 
                             evidence: Optional[str] = None,
                             concerns: Optional[List[str]] = None) -> Dict:
        """Create a standardized error response."""
        return {
            "verified": verified,
            "matches_answer": matches_answer,
            "confidence": confidence,
            "analysis": error_message,
            "correct_answer": correct_answer,
            "evidence": evidence,
            "concerns": concerns or []
        }
    
    def _call_openai_vision(self, prompt: str, photos: List[str], max_tokens: int = 500) -> Dict:
        """
        Common method for making OpenAI Vision API calls.
        
        Args:
            prompt: The prompt to send to the API
            photos: List of photo URLs
            max_tokens: Maximum tokens for the response
            
        Returns:
            Dict containing the API response or error
        """
        try:
            # Create message for vision API
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *[{
                            "type": "image_url",
                            "image_url": {"url": photo}
                        } for photo in photos]
                    ]
                }
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Parse and return the response
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            error_msg = f"Error calling OpenAI Vision API: {str(e)}"
            print(error_msg)
            return {"error": error_msg}

    def validate_photos(self, photos: List[str], question: str) -> Dict:
        """
        Validate photos for a risk question using OpenAI's Vision API.
        
        Args:
            photos: List of photo URLs
            question: The risk question being validated
            
        Returns:
            Dict containing validation results
        """
        prompt = f"""Analyze these photos in relation to the following question:
        {question}
        
        Look for:
        1. Clear visibility of the relevant area/feature
        2. Evidence supporting or contradicting the answer
        3. Any safety concerns visible in the photos
        
        Respond with a JSON object containing:
        {{
            "is_valid": boolean,  // whether the photos adequately show what's needed
            "analysis": string,   // brief explanation of what's visible
            "concerns": string[]  // list of any safety concerns spotted
        }}
        """
        
        result = self._call_openai_vision(prompt, photos, max_tokens=500)
        
        if "error" in result:
            return {
                "is_valid": False,
                "analysis": result["error"],
                "concerns": []
            }
        
        return result

    def verify_answer(self, photos: List[str], question: str, user_answer: str, rubric: Dict[str, int]) -> Dict:
        """
        Verify if the user's answer matches what's visible in the photos.
        
        Args:
            photos: List of photo URLs
            question: The risk question being validated
            user_answer: The user's answer to the question
            rubric: The scoring rubric for the question (e.g. {"Yes": 1, "No": 0})
            
        Returns:
            Dict containing verification results
        """
        # Check if photo validation is required
        if not self._requires_photo_validation(user_answer, rubric):
            return self._create_error_response(
                error_message="Photo validation skipped - user admitted to risk",
                verified=True,
                matches_answer=True,
                confidence=1.0,
                correct_answer=user_answer,
                evidence="User's answer indicates presence of risk, no photo validation needed"
            )

        # First validate that the photos are adequate
        validation = self.validate_photos(photos, question)
        if not validation["is_valid"]:
            return self._create_error_response(
                error_message="Photos do not adequately show what's needed for verification",
                evidence=validation["analysis"],
                concerns=validation["concerns"]
            )
        
        # Prepare the verification prompt
        prompt = f"""Analyze these photos to verify the following question and answer:

        Question: {question}
        User's Answer: {user_answer}
        Valid Answers: {list(rubric.keys())}

        Your task:
        1. Determine if the photos show clear evidence to verify or contradict the user's answer
        2. Based on what's visible in the photos, what should the correct answer be?
        3. Provide specific evidence from the photos to support your determination
        4. Rate your confidence in your assessment (0.0 to 1.0)

        Respond with a JSON object containing:
        {{
            "verified": boolean,        // whether there's enough evidence to make a determination
            "matches_answer": boolean,  // whether the user's answer matches what's visible
            "confidence": float,        // confidence level (0.0 to 1.0)
            "analysis": string,         // explanation of your determination
            "correct_answer": string,   // what the answer should be based on the photos
            "evidence": string,         // specific evidence from the photos
            "concerns": string[]        // any additional safety concerns spotted
        }}
        """
        
        result = self._call_openai_vision(prompt, photos, max_tokens=1000)
        
        if "error" in result:
            return self._create_error_response(result["error"])
        
        return result
            
def main():
    """Example usage of RiskPhotoManager and RiskPhotoValidator."""
    # Initialize the classes
    photo_manager = RiskPhotoManager()
    validator = RiskPhotoValidator()
    
    # Example usage
    question = "Are there any tree limbs or branches hanging over your home?"
    question_id = "tree_limbs_over_home"
    user_id = "test_user_123"
    user_answer = "No"
    rubric = {"Yes": 0, "No": 1}
    
    # Example: Upload a photo
    with open("rough_notebooks/example_photo.jpg", "rb") as f:
        photo_data = f.read()
        photo_url = photo_manager.upload_photo(photo_data, question_id, user_id)
        
    if photo_url:
        # Get all photos for this question
        photos = photo_manager.get_photos_for_question(question_id, user_id)
        
        # Verify the user's answer
        verification_result = validator.verify_answer(photos, question, user_answer, rubric)
        
        print("Verification Result:")
        print(json.dumps(verification_result, indent=2))
        
if __name__ == "__main__":
    main()
