"""
Module for generating improvement recommendations based on risk assessment scores.
"""
from typing import Dict, List, Optional

class RecommendationEngine:
    def __init__(self):
        """Initialize the recommendation engine."""
        self.top_recommendations: List[Dict] = []  # Store top recommendations

    def get_improvement_recommendations(self, grader_results: Dict) -> List[Dict]:
        """
        Generate improvement recommendations based on questions that didn't score 100%.
        Questions are sorted by score (ascending) and then by points possible (descending)
        to prioritize the most impactful improvements first.
        
        Args:
            grader_results: The output dictionary from RiskGrader.calculate_score()
            
        Returns:
            List of dictionaries containing:
                - question: The question text
                - risk_type: The associated risk category
                - risk_level: The risk level for this category
                - importance: Importance level for this risk
                - current_answer: The user's current answer
                - current_score: The current score percentage
                - points_possible: Maximum points possible for this question
                - points_earned: Current points earned for this question
                - requires_photo: Whether photo validation is required
                - photo_validated: Whether photo validation was performed
        """
        # Get questions that didn't score 100%
        recommendations = [
            question for question in grader_results['question_scores']
            if question['score_percentage'] < 100
        ]
        
        # Store top 3 recommendations if available
        self.top_recommendations = recommendations[:3] if recommendations else []
        
        # Questions are already sorted by score_percentage (ascending) and points_possible (descending)
        # from the grader output, so we can return them as is
        return recommendations

    def get_top_recommendations(self, limit: int = 3) -> List[Dict]:
        """
        Get the top recommendations (up to the specified limit).
        These are the questions with the lowest scores and highest possible points.
        
        Args:
            limit: Maximum number of recommendations to return (default 3)
            
        Returns:
            List of the top recommendation dictionaries, sorted by priority
        """
        return self.top_recommendations[:limit]

    def format_recommendations(self, recommendations: List[Dict], show_limit: Optional[int] = None) -> str:
        """
        Format the recommendations into a human-readable string.
        
        Args:
            recommendations: List of recommendation dictionaries from get_improvement_recommendations()
            show_limit: Optional limit on number of recommendations to show
            
        Returns:
            Formatted string containing the recommendations
        """
        if not recommendations:
            return "Great job! All questions scored 100%. No improvements needed."
            
        output = []
        output.append("Recommended Improvements:")
        output.append("-" * 50)
        
        # Apply limit if specified
        recommendations_to_show = recommendations[:show_limit] if show_limit else recommendations
        
        for i, rec in enumerate(recommendations_to_show, 1):
            output.append(f"\n{i}. Question: {rec['question']}")
            output.append(f"   Risk Type: {rec['risk_type']} (Level: {rec['risk_level']}, Importance: {rec['importance']})")
            output.append(f"   Current Score: {rec['score_percentage']:.2f}%")
            output.append(f"   Points: {rec['points_earned']:.2f} / {rec['points_possible']:.2f}")
            output.append(f"   Current Answer: {rec['answer']}")
            
            if rec['requires_photo']:
                if rec['photo_validated']:
                    output.append("   * Photo validation was performed")
                else:
                    output.append("   * Photo validation required but not performed")
                    
        if show_limit and len(recommendations) > show_limit:
            output.append(f"\n... and {len(recommendations) - show_limit} more recommendations.")
                    
        return "\n".join(output)

def main():
    """Example usage of RecommendationEngine."""
    from grader import RiskGrader
    
    # Initialize the classes
    grader = RiskGrader()
    recommendation_engine = RecommendationEngine()
    
    # Example answers (matching the format from QuestionMaster)
    example_answers = [
        {
            'question': 'Is your basement properly sealed and waterproofed?',
            'risk_type': 'Flooding',
            'importance': 'High',
            'answer': 'No',  # Incorrect answer
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High'
        },
        {
            'question': 'Do you have a sump pump installed in your home?',
            'risk_type': 'Flooding',
            'importance': 'High',
            'answer': 'No',  # Incorrect answer
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Very High'
        },
        {
            'question': 'Does your roof have any shingles that are missing, cracked, curled or otherwise damaged?',
            'risk_type': 'Winter',
            'importance': 'High',
            'answer': 'Yes',  # Incorrect answer (Yes indicates risk)
            'rubric': {'Yes': 0, 'No': 1},
            'risk_level': 'Very High'
        },
        {
            'question': 'Are your gutters clear of debris?',
            'risk_type': 'Winter',
            'importance': 'High',
            'answer': 'Yes',  # Correct answer
            'rubric': {'Yes': 1, 'No': 0},
            'risk_level': 'Relatively High',
            'photos': ['https://example.com/photo1.jpg']
        }
    ]
    
    # Calculate scores
    results = grader.calculate_score(example_answers)
    
    # Get all recommendations
    all_recommendations = recommendation_engine.get_improvement_recommendations(results)
    print("\nAll Recommendations:")
    print(recommendation_engine.format_recommendations(all_recommendations))
    
    # Get and show top 3 recommendations
    top_recommendations = recommendation_engine.get_top_recommendations()
    print("\nTop 3 Priority Recommendations:")
    print(recommendation_engine.format_recommendations(top_recommendations))

if __name__ == '__main__':
    main()
