import os
from typing import Any, Optional, List

from dotenv import load_dotenv
from elevenlabs import ConversationalConfig, ElevenLabs, TwilioOutboundCallResponse

from config import INITIAL_MESSAGE, SYSTEM_PROMPT


load_dotenv()


class DispatchAgent:
    def __init__(self, agent_id: str, agent_phone_number_id: str):
        self.client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )
        self.agent_id = agent_id
        self.agent_phone_number_id = agent_phone_number_id
        self.conversations = []

    def _create_agent(self):
        # TODO: Can a single agent be used for multiple calls?
        id = self.client.conversational_ai.agents.create(
            conversation_config=ConversationalConfig(),
        )
        return id

    def get_conversation_details(self, conversation_id: str):
        return self.client.conversational_ai.conversations.get(
            conversation_id=conversation_id
        )
    
    def make_call(
            self,
            phone_number: str,
            customer_name: str,
            business_name: str
        ) -> TwilioOutboundCallResponse:
        response = self.client.conversational_ai.twilio.outbound_call(
            agent_id=self.agent_id,
            agent_phone_number_id=self.agent_phone_number_id,
            to_number=phone_number,
            conversation_initiation_client_data={
                "conversation_config_override": {
                    "agent": {
                        "first_message": INITIAL_MESSAGE.format(
                            name=customer_name,
                            business_name=business_name
                        ),
                        # "prompt": SYSTEM_PROMPT,
                    }
                }
            }
        )
        self.conversations.append(response.conversation_id)
        return response
    
    def check_help_identified(self, conversation_id: str) -> Optional[Any]:
        conversation_details = self.get_conversation_details(conversation_id)

        # TODO: Tract through the call contents and look for keywords
        # like available, not available, etc.
        # TODO: This should include a list or dict of relevant items for
        # the action graph. E.g. price, timing, etc.
        return None
    
    # def make_batch_call(
    #         self, 
    #         call_name: str, 
    #         phone_numbers: list[str]
    #     ):
    #     recipients = [
    #         OutboundCallRecipient(
    #             phone_number=phone_number,
    #         )
    #         for phone_number in phone_numbers
    #     ]
    #     # TODO: Twilio allows for 1 call per second, but calls are queued and executed in order
    #     # TODO: This would mean we could potentially have a very long queue of calls if multiiple
    #     # TODO: areas have detected anomalies.
    #     self.client.conversational_ai.batch_calls.create(
    #         call_name=call_name,
    #         agent_id=self.agent_id,
    #         agent_phone_number_id=self.agent_phone_number_id,
    #         recipients=recipients,
    #     )


