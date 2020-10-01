import os
import json
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

message = "who is wang dayuan"

def watson_call(message):
    authenticator = IAMAuthenticator(os.environ['WATSON_ASSISTANT_API_KEY'])
    assistant = AssistantV2(
        version='2020-04-01',
        authenticator=authenticator
    )
    assistant.set_service_url(os.environ['WATSON_ASSISTANT_URL'])

    response = assistant.message_stateless(
        assistant_id=os.environ['WATSON_ASSISTANT_ID'],
        input={
            'message_type': 'text',
            'text': message

        }).get_result()
    print(json.dumps(response, indent=2))

watson_call(message)