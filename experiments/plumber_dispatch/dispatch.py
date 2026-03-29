from typing import Optional
import time

from agent import DispatchAgent
from search import ProximitySearch
from graph import Graph


class Dispatch:
    """
    Dispatches a call to a business in the given location and
    organizes relevant parties to create a list of action items and
    resolve the issue.
    """
    def __init__(self, dispatch_agent: DispatchAgent, proximity_searcher: ProximitySearch):
        self.dispatch_agent = dispatch_agent
        self.proximity_searcher = proximity_searcher

    def _check_call_status(self, conversation_id: str) -> bool:
        conversation_details = self.dispatch_agent.get_conversation_details(conversation_id)
        if conversation_details.status == "completed":
            return True
        return False

    def _create_action_graph(self, results: list[dict]) -> Optional[Graph]:
        return None

    def dispatch(self, location: str):
        calling_list = self.proximity_searcher.generate_calling_list(location)

        help_found = False
        idx = 0

        while not help_found and idx < len(calling_list):
            response = self.dispatch_agent.make_call(
                # phone_number=calling_list[idx]['phone'],
                phone_number='+12899716341', # Temporary phone number for testing
                customer_name="Michael Dawes", # TODO: Get this from the user
                business_name=calling_list[idx]['business_name']
            )
            time.sleep(120) # Assuming call will take 2 minutes
            call_complete = self._check_call_status(response.conversation_id)
            if call_complete:
                help_found = self.dispatch_agent.check_help_identified(response.conversation_id)
                if help_found:
                    # TODO: There should be some sort of HITL here to ensure they have a point of contact
                    action_graph = self._create_action_graph(help_found)
                    return action_graph
                else:
                    idx += 1
        return None
    
    