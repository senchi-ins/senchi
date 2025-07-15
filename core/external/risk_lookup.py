"""
Risk lookup module for identifying catastrophic risks based on location.
"""
import pandas as pd
from typing import Dict, List, Mapping, Optional, Union
from pathlib import Path

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
    
    def __init__(self, nri_data_path: str = '../external/data/NRI_Ratings_Counties.csv',
                 canada_data_path: str = '../external/data/canada_risk.csv'):
        """
        Initialize the risk lookup with NRI data and Canadian risk data.
        
        Args:
            nri_data_path: Path to the NRI ratings CSV file
            canada_data_path: Path to the Canadian risk ratings CSV file
        """
        # Load USA data
        self.nri_data = pd.read_csv(nri_data_path)
        # Preprocess the reference data
        self.nri_data['COUNTY'] = self.nri_data['COUNTY'].str.strip().str.lower()
        self.nri_data['STATEABBRV'] = self.nri_data['STATEABBRV'].str.strip().str.lower()
        
        # Load Canadian data
        self.canada_data = pd.read_csv(canada_data_path)
        # Preprocess Canadian data
        self.canada_data['Province'] = self.canada_data['Province'].str.strip()
        self.canada_data['Region'] = self.canada_data['Region'].str.strip()
        
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
                    'province': str (Canada only),
                    'region': str (Canada only, administrative area level 2)
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
        # Find the region data
        region_data = self.canada_data[
            (self.canada_data['Province'] == location_data['province']) &
            (self.canada_data['Region'] == location_data['region'])
        ]
        
        if region_data.empty:
            # Return message about automated risk detection not being available
            error_msg = f"Automated risk detection currently not implemented for {location_data['formatted_address']}"
            raise ValueError(error_msg)
            
        # Initialize results with all categories
        risks = {category: None for category in RISK_CATEGORIES.keys()}
        
        # For Canadian data, we directly map the categories without risk codes
        for category in RISK_CATEGORIES.keys():
            if category in region_data.columns:
                rating = region_data[category].iloc[0]
                if rating in RISK_RATINGS:
                    risks[category] = rating
                    
        return risks
