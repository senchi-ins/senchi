"""
Module for generating risk-specific questions based on location risk assessment.
"""
import json
from typing import Dict, List, Optional, Set
from pathlib import Path

from .risk_lookup import RISK_RATINGS, RiskLookup

class QuestionMaster:
    def __init__(self, questions_path: str = '../external/risk_questions.json'):
        """
        Initialize QuestionMaster with risk questions data.
        
        Args:
            questions_path: Path to the risk questions JSON file
        """
        # Load questions data
        questions_file = Path(__file__).parent / questions_path
        with open(questions_file, 'r') as f:
            self.questions_data = json.load(f)
            
        # Pre-process questions by risk category for faster lookup
        # TODO: Is this needed? Can I just read in the json and use as is?
        # TODO: Rather than getting questions by risk, filter the questions based on the 
        # specific risk in the persons area (since we already need location data) using the `*.csv` files
        self.questions_by_risk = {}
        for question in self.questions_data['risk_questions']:
            for risk_type, importance in zip(question['risk'], question['importance']):
                if risk_type not in self.questions_by_risk:
                    self.questions_by_risk[risk_type] = []
                self.questions_by_risk[risk_type].append({
                    'question': question['question'],
                    'importance': importance,
                    'rubric': question['rubric']
                })

    # TODO: Delete this function, relevant questions are now filtered based on the risk in the persons area
    def get_relevant_questions(self, risk_assessment: Dict[str, Optional[str]]) -> List[Dict]:
        """
        Generate a list of unique relevant questions based on high-risk events.
        If a question applies to multiple risk categories, it will only appear once
        in the output list.
        
        Args:
            risk_assessment: Dictionary mapping risk categories to their risk levels
                           (output from RiskLookup.get_location_risks)
                
        Returns:
            List of unique question dictionaries containing:
                - question: The question text
                - risk_type: The associated risk category (primary category if multiple)
                - importance: Importance level for this risk (highest importance if multiple)
                - rubric: Valid answers and their scores
                - all_risk_types: List of all risk types this question applies to
                - all_importance_levels: List of importance levels for each risk type
        """
        high_risk_questions = []
        seen_questions: Set[str] = set()  # Track unique questions by text
        
        # Map risk lookup categories to question categories
        risk_category_map = {
            'Flooding': 'Flooding',
            'Cold Wave / Severe Winter Weather': 'Winter',
            'Hail': 'Hail',
            'Wildfire': 'Wildfire',
            'Wind': 'Wind',
            'Earthquake': 'Earthquake'
        }
        
        # Only process risks rated as Very High or Relatively High
        high_risk_levels = {RISK_RATINGS[0], RISK_RATINGS[1]}  # Very High, Relatively High
        
        # First, collect all questions with their risk types and importance levels
        questions_data = {}  # Dict to store question data keyed by question text
        
        for risk_category, risk_level in risk_assessment.items():
            if risk_level in high_risk_levels:
                # Map the risk lookup category to question category
                question_category = risk_category_map.get(risk_category)
                if not question_category:
                    continue
                    
                # Get questions for this risk category
                risk_questions = self.questions_by_risk.get(question_category, [])
                
                # Process each question
                for question in risk_questions:
                    question_text = question['question']
                    
                    if question_text not in questions_data:
                        questions_data[question_text] = {
                            'question': question_text,
                            'risk_types': [],
                            'importance_levels': [],
                            'rubric': question['rubric']
                        }
                    
                    questions_data[question_text]['risk_types'].append(question_category)
                    questions_data[question_text]['importance_levels'].append(question['importance'])
        
        # Convert collected data into final format
        for question_info in questions_data.values():
            # Get the highest importance level
            importance_ranks = {'High': 0, 'Medium': 1, 'Low': 2}
            sorted_importance = sorted(
                question_info['importance_levels'],
                key=lambda x: importance_ranks.get(x, 3)
            )
            primary_importance = sorted_importance[0] if sorted_importance else 'High'
            
            # Use the risk type associated with the highest importance as primary
            primary_idx = question_info['importance_levels'].index(primary_importance)
            primary_risk_type = question_info['risk_types'][primary_idx]
            
            high_risk_questions.append({
                'question': question_info['question'],
                'risk_type': primary_risk_type,
                'importance': primary_importance,
                'rubric': question_info['rubric'],
                'all_risk_types': question_info['risk_types'],
                'all_importance_levels': question_info['importance_levels']
            })
        
        return high_risk_questions

# TODO: Delete this function
def main():
    """Example usage of QuestionMaster."""
    # Initialize the classes
    risk_lookup = RiskLookup()
    question_master = QuestionMaster()
    
    # Example location data
    location_data = {
        'country': 'USA',
        'county': 'Miami-Dade',
        'state': 'fl',
        'address': '123 Main St',
        'latitude': 25.7617,
        'longitude': -80.1918
    }
    
    # Get risk assessment
    risks = dict(risk_lookup.get_location_risks(location_data))  # Convert Mapping to Dict
    
    # Get relevant questions
    questions = question_master.get_relevant_questions(risks)
    
    # Print results
    print(f"Found {len(questions)} unique questions for high-risk events:")
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        print(f"   Primary Risk Type: {q['risk_type']}")
        print(f"   Primary Importance: {q['importance']}")
        print(f"   All Risk Types: {', '.join(q['all_risk_types'])}")
        print(f"   All Importance Levels: {', '.join(q['all_importance_levels'])}")
        print(f"   Scoring: {q['rubric']}")

if __name__ == '__main__':
    main()
