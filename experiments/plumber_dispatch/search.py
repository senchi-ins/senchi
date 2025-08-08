import os
from serpapi import GoogleSearch    
from dotenv import load_dotenv

from utils import format_phone_number

load_dotenv()


class ProximitySearch:
    """
    Searches for a given business within a given location
    and generates a list of businesses to call.
    """

    def __init__(self, base_query: str = "Plumbers near"):
        self.search_api_key = os.getenv("SERPAPI_API_KEY")
        self.base_query = base_query
        self.results = []

    def _search_serp(self, query: str, location: str) -> dict:
        params = {
            "q": query,
            "location": location,
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com",
            "api_key": self.search_api_key
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        return results["local_results"]

    def _find_nearby(self, location: str) -> list[dict]:
        query = f"{self.base_query} {location}"
        results = self._search_serp(query, location)

        # TODO: Get a larger list of results by clicking the 'more_locations_link
        res = []
        for result in results['places']:
            res.append({
                "business_name": result['title'],
                "type": result['type'],
                "years_in_business": result['years_in_business'],
                "address": result['address'],
                "phone": format_phone_number(result['phone']),
                "website": result['links']['website'],
                'location': (result['gps_coordinates']['latitude'], result['gps_coordinates']['longitude']),
                "hours": result['hours'],
            })
        return res

    def generate_calling_list(self, location: str) -> list[dict]:
        calling_list = []
        for result in self._find_nearby(location):
            calling_list.append({
                "business_name": result['business_name'],
                "phone": result['phone'],
            })
        return calling_list