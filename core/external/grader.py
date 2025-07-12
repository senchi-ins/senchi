"""
Module for grading risk assessment answers based on risk levels and scoring criteria.
"""
import json
from pathlib import Path
from typing import Dict, List, Union

from .risk_lookup import RISK_RATINGS

class RiskGrader:
    def __init__(self, scoring_path: str = 'scoring.json'):
        """
        Initialize RiskGrader with scoring criteria.
        
        Args:
            scoring_path: Path to the scoring criteria JSON file
        """
        # Load scoring criteria
        scoring_file = Path(__file__).parent / scoring_path
        with open(scoring_file, 'r') as f:
            self.scoring_criteria = json.load(f)

    def calculate_score(self, answers: List[Dict]) -> Dict:
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
                
        Returns:
            Dictionary containing:
                - total_score: The final score as a percentage
                - points_earned: Total points earned
                - points_possible: Total points possible
                - breakdown: Dictionary of scores by risk level
        """
        points_earned = 0
        points_possible = 0
        breakdown = {level: {'earned': 0, 'possible': 0} for level in RISK_RATINGS}
        
        for answer_data in answers:
            risk_level = answer_data['risk_level']
            importance = answer_data['importance']
            rubric = answer_data['rubric']
            answer = answer_data['answer']
            
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
            }.get(importance, 1.0)
            
            question_points = base_points * importance_multiplier
            
            # Calculate points for this question
            if answer in rubric:
                binary_score = rubric[answer]  # Will be 1 or 0
                earned = question_points * binary_score
                points_earned += earned
                points_possible += question_points
                
                # Update breakdown
                breakdown[risk_level]['earned'] += earned
                breakdown[risk_level]['possible'] += question_points
        
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
            }
        }

def main():
    """Example usage of RiskGrader."""
    grader = RiskGrader()
    
    # Example answers (matching the format from QuestionMaster)
    example_answers = [
        {
            'question': 'Are all major systems elevated at least 1 foot above the ground?',
            'risk_type': 'Flooding',
            'importance': 'High',
            'answer': 'Yes',
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High'
        },
        {
            'question': 'Do you have a sump pump installed in your home?',
            'risk_type': 'Flooding',
            'importance': 'High',
            'answer': 'No',
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High'
        },
        {
            'question': 'Is your basement properly sealed and waterproofed?',
            'risk_type': 'Flooding',
            'importance': 'High',
            'answer': 'Yes',
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Relatively High'
        }
    ]
    
    # Calculate and display results
    results = grader.calculate_score(example_answers)
    
    print(f"\nFinal Score: {results['total_score']}%")
    print(f"Points Earned: {results['points_earned']} out of {results['points_possible']}")
    print("\nBreakdown by Risk Level:")
    for level, stats in results['breakdown'].items():
        print(f"\n{level}:")
        print(f"  Earned: {stats['earned']} points")
        print(f"  Possible: {stats['possible']} points")
        print(f"  Score: {stats['percentage']}%")

if __name__ == '__main__':
    main()
