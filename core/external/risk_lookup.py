"""
Risk lookup module for identifying catastrophic risks based on location.
"""
import pandas as pd
from typing import Dict, List, Mapping, Optional, Union

# Risk category mappings
RISK_CATEGORIES = {
    'Flooding': ['CFLD_RISKR', 'LTNG_RISKR', 'RFLD_RISKR', 'TSUN_RISKR'],
    'Cold Wave / Severe Winter Weather': ['AVLN_RISKR', 'CWAV_RISKR', 'ISTM_RISKR', 'WNTW_RISKR'],
    'Hail': ['HAIL_RISKR'],
    'Wildfire': ['WFIR_RISKR'],
    'Wind': ['HRCN_RISKR', 'SWND_RISKR', 'TRND_RISKR'],
    'Earthquake': ['ERQK_RISKR']
    # ['LNDS_RISKR', 'VLCN_RISKR', 'DRGT_RISKR', 'HWAV_RISKR'] (Landslide, Volcano, Drought, Heat Wave) not applicable yet
}

# Risk ratings in order from highest to lowest
RISK_RATINGS = [
    'Very High',
    'Relatively High',
    'Relatively Moderate',
    'Relatively Low'
]

class RiskLookup:
    """Handles risk assessment based on location data."""
    
    def __init__(self, nri_data_path: str = '../../external/NRI_Ratings_Counties.csv'):
        """
        Initialize the risk lookup with NRI data.
        
        Args:
            nri_data_path: Path to the NRI ratings CSV file
        """
        self.nri_data = pd.read_csv(nri_data_path)
        # Preprocess the reference data
        self.nri_data['COUNTY'] = self.nri_data['COUNTY'].str.strip().str.lower()
        self.nri_data['STATEABBRV'] = self.nri_data['STATEABBRV'].str.strip().str.lower()
        
    def _normalize_string(self, value: str) -> str:
        """
        Normalize a string by removing whitespace and converting to lowercase.
        
        Args:
            value: String to normalize
            
        Returns:
            Normalized string
        """
        return value.strip().lower()
        
    def get_location_risks(self, location_data: Dict) -> Mapping[str, Optional[str]]:
        """
        Get risks for a location based on geocoded address data.
        
        Args:
            location_data: Dictionary containing geocoded address information
                Expected format:
                {
                    'address': str,
                    'latitude': float,
                    'longitude': float,
                    'formatted_address': str,
                    'country': str,
                    'county': str (USA only),
                    'state': str (USA only),
                    'province': str (Canada only)
                }
                
        Returns:
            Dictionary mapping risk categories to their highest risk level (or None if no significant risks)
        """
        if location_data['country'] == 'USA':
            # Normalize just the county and state for matching
            location_data = location_data.copy()
            location_data['county'] = self._normalize_string(location_data['county'])
            location_data['state'] = self._normalize_string(location_data['state'])
            return self._get_usa_risks(location_data)
        elif location_data['country'] == 'Canada':
            return self._get_canada_risks(location_data)
        else:
            raise ValueError(f"Unsupported country: {location_data['country']}")
            
    def _get_usa_risks(self, location_data: Dict) -> Mapping[str, Optional[str]]:
        """Get risks for a USA location."""
        # Find the county data
        county_data = self.nri_data[
            (self.nri_data['COUNTY'] == location_data['county']) &
            (self.nri_data['STATEABBRV'] == location_data['state'])
        ]
        
        if county_data.empty:
            # Try to find similar matches for debugging
            possible_counties = self.nri_data[
                self.nri_data['STATEABBRV'] == location_data['state']
            ]['COUNTY'].unique()
            
            error_msg = f"No data found for {location_data['county']} County, {location_data['state'].upper()}"
            if len(possible_counties) > 0:
                error_msg += f"\nAvailable counties in {location_data['state'].upper()}: {', '.join(sorted(possible_counties))}"
            raise ValueError(error_msg)
            
        # Initialize results with all categories
        risks = {category: None for category in RISK_CATEGORIES.keys()}
        
        # Check each risk category
        for category, risk_codes in RISK_CATEGORIES.items():
            highest_rating = None
            
            # Check each risk code in the category
            for code in risk_codes:
                if code in county_data.columns:
                    rating = county_data[code].iloc[0]
                    if rating in RISK_RATINGS:
                        # Update highest_rating if this rating is higher
                        current_index = RISK_RATINGS.index(rating) if rating in RISK_RATINGS else -1
                        highest_index = RISK_RATINGS.index(highest_rating) if highest_rating in RISK_RATINGS else -1
                        
                        if highest_rating is None or (current_index >= 0 and current_index < highest_index):
                            highest_rating = rating
            
            # Set the highest rating found for this category
            risks[category] = highest_rating
                
        return risks
        
    def _get_canada_risks(self, location_data: Dict) -> Mapping[str, Optional[str]]:
        """Get risks for a Canadian location."""
        # TODO: Implement Canadian risk assessment
        return {category: None for category in RISK_CATEGORIES.keys()}
