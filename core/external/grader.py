"""
Module for grading risk assessment answers based on risk levels and scoring criteria.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from .risk_lookup import RISK_RATINGS
from .camera import RiskPhotoValidator

class RiskGrader:
    def __init__(self, scoring_path: str = '../external/scoring.json', questions_path: str = '../external/risk_questions.json'):
        """
        Initialize RiskGrader with scoring criteria.
        
        Args:
            scoring_path: Path to the scoring criteria JSON file
            questions_path: Path to the risk questions JSON file
        """
        # Load scoring criteria
        scoring_file = Path(__file__).parent / scoring_path
        with open(scoring_file, 'r') as f:
            self.scoring_criteria = json.load(f)
            
        # Load questions data to check which ones require photos
        questions_file = Path(__file__).parent / questions_path
        with open(questions_file, 'r') as f:
            questions_data = json.load(f)
            self.photo_required_questions = {
                q['question']: q['requires_photo']
                for q in questions_data['risk_questions']
            }
            
        # Initialize photo validator
        self.photo_validator = RiskPhotoValidator()

    def calculate_score(self, answers: List[Dict], user_id: Optional[str] = None) -> Dict:
        """
        Calculate the final score based on answers to risk questions.
        
        Args:
            answers: List of dictionaries containing:
                - question: The question text
                - risk_type: The associated risk category
                - importance: Importance level for this risk
                - answer: The user's answer (should match a key in the rubric)
                - rubric: The scoring rubric for the question
                - risk_level: The risk level for this category (e.g., "Very High")
                - photos: Optional list of photo URLs for validation
                
            user_id: Optional user identifier for photo validation
                
        Returns:
            Dictionary containing:
                - total_score: The final score as a percentage
                - points_earned: Total points earned
                - points_possible: Total points possible
                - breakdown: Dictionary of scores by risk level
                - photo_validations: Dictionary of photo validation results by question
                - question_scores: List of dictionaries containing per-question scores and details
        """
        points_earned = 0
        points_possible = 0
        breakdown = {level: {'earned': 0, 'possible': 0} for level in RISK_RATINGS}
        photo_validations = {}
        question_scores = []  # New list to store individual question scores
        
        for answer_data in answers:
            risk_level = answer_data['risk_level']
            importance = answer_data['importance']
            rubric = answer_data['rubric']
            answer = answer_data['answer']
            question = answer_data['question']
            risk_type = answer_data['risk_type']
            
            # Skip if risk level not in scoring criteria
            if risk_level not in self.scoring_criteria:
                continue
                
            # Get base points for this risk level
            base_points = self.scoring_criteria[risk_level][0]['1']
            
            # Adjust points based on importance
            importance_multiplier = {
                'High': 1.0,
                'Medium': 0.7,
                'Low': 0.4
            }.get(importance, 0.7)
            
            question_points = base_points * importance_multiplier
            
            # Check if this question requires photo validation
            requires_photo = self.photo_required_questions.get(question, False)
            photos = answer_data.get('photos', [])
            
            # Skip photo validation if user admits to risk
            needs_validation = requires_photo and self.photo_validator._requires_photo_validation(answer, rubric)
            
            # Initialize question score data
            question_score_data = {
                'question': question,
                'risk_type': risk_type,
                'risk_level': risk_level,
                'importance': importance,
                'answer': answer,
                'points_possible': question_points,
                'requires_photo': requires_photo,
                'photo_validated': False
            }
            
            if needs_validation and photos:
                # Validate photos and adjust score accordingly
                validation = self.photo_validator.verify_answer(photos, question, answer, rubric)
                photo_validations[question] = validation
                question_score_data['photo_validated'] = True
                
                if validation['verified']:
                    if validation['matches_answer']:
                        # Answer matches photo evidence - full points
                        binary_score = rubric[answer]
                        earned = question_points * binary_score
                    else:
                        # Photo evidence contradicts answer - no points
                        earned = 0
                else:
                    # Couldn't verify from photos - partial credit if answer claims no risk
                    binary_score = rubric[answer]
                    if binary_score == 1:  # Answer claims no risk
                        earned = question_points * 0.5  # 50% credit
                    else:
                        earned = 0  # No credit if claiming risk but can't verify
                
                points_earned += earned
                points_possible += question_points
                
                # Update breakdown
                breakdown[risk_level]['earned'] += earned
                breakdown[risk_level]['possible'] += question_points
                
            elif answer in rubric:
                # No photo required, no photos provided, or user admits to risk - score normally
                binary_score = rubric[answer]
                earned = question_points * binary_score
                points_earned += earned
                points_possible += question_points
                
                # Update breakdown
                breakdown[risk_level]['earned'] += earned
                breakdown[risk_level]['possible'] += question_points
            
            # Add earned points and score percentage to question data
            question_score_data['points_earned'] = earned
            question_score_data['score_percentage'] = (earned / question_points * 100) if question_points > 0 else 0
            question_scores.append(question_score_data)
        
        # Calculate final percentage score
        final_score = (points_earned / points_possible * 100) if points_possible > 0 else 0
        
        return {
            'total_score': round(final_score, 2),
            'points_earned': round(points_earned, 2),
            'points_possible': round(points_possible, 2),
            'breakdown': {
                level: {
                    'earned': round(stats['earned'], 2),
                    'possible': round(stats['possible'], 2),
                    'percentage': round((stats['earned'] / stats['possible'] * 100) if stats['possible'] > 0 else 0, 2)
                }
                for level, stats in breakdown.items()
                if stats['possible'] > 0  # Only include risk levels that had questions
            },
            'photo_validations': photo_validations,
            'question_scores': sorted(
                question_scores,
                key=lambda x: (x['score_percentage'], -x['points_possible'])  # Sort by score (ascending) and then by points possible (descending)
            )
        }

# TODO: Delete this function
def main():
    """Example usage of RiskGrader."""
    grader = RiskGrader()
    
    # Example answers (matching the format from QuestionMaster)
    example_answers = [
        {
            'question': 'Are there any tree limbs or branches that are hanging over your home?',
            'risk_type': 'Winter',
            'importance': 'High',
            'answer': 'Yes',  # Admits to risk - no photo validation needed
            'rubric': {'Yes': 0, 'No': 1},
            'risk_level': 'Very High',
            'photos': ['https://example.com/photo1.jpg']  # Photo will be ignored
        },
        {
            'question': 'Are your eavesdrops, drains, gutters, and roof free of debris?',
            'risk_type': 'Winter',
            'importance': 'High',
            'answer': 'Yes',  # Claims no risk - needs photo validation
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High',
            'photos': ['https://example.com/photo2.jpg']  # Photo will be validated
        }
    ]
    
    # Calculate and display results
    results = grader.calculate_score(example_answers, user_id='test_user')
    
    print(f"\nFinal Score: {results['total_score']}%")
    print(f"Points Earned: {results['points_earned']} out of {results['points_possible']}")
    print("\nBreakdown by Risk Level:")
    for level, stats in results['breakdown'].items():
        print(f"\n{level}:")
        print(f"  Earned: {stats['earned']} points")
        print(f"  Possible: {stats['possible']} points")
        print(f"  Score: {stats['percentage']}%")
        
    if results['photo_validations']:
        print("\nPhoto Validation Results:")
        for question, validation in results['photo_validations'].items():
            print(f"\n{question}:")
            print(f"  Verified: {validation['verified']}")
            print(f"  Matches Answer: {validation['matches_answer']}")
            print(f"  Confidence: {validation['confidence']}")
            print(f"  Analysis: {validation['analysis']}")
            
    print("\nQuestion Scores:")
    for q_score in results['question_scores']:
        print(f"\n{q_score['question']}:")
        print(f"  Risk Type: {q_score['risk_type']}")
        print(f"  Risk Level: {q_score['risk_level']}")
        print(f"  Importance: {q_score['importance']}")
        print(f"  Score: {q_score['score_percentage']}%")
        print(f"  Points: {q_score['points_earned']} / {q_score['points_possible']}")

if __name__ == '__main__':
    main()
