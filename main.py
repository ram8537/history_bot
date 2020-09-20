import os
import json
from flask import Flask, request
import requests
import threading
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

app = Flask(__name__)


@app.route('/', methods=['POST'])
def validation():
    content = (request.form)
    content_text = request.form.get('text')
    content_response_url = request.form.get('response_url')
    print(f"content = {content} ")
    print(f"content text = {content_text} ")
    print(f"content response_url = {content_response_url}")

    thr = threading.Thread(
        target=watson_call,
        args=(content_text, content_response_url)
    )
    thr.start()

    return "hold on...", 200


def watson_call(content_text, content_response_url):
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
            'text': f'{content_text}'
        }).get_result()

    try:
        filtered_response = response['output']['user_defined']['personal_api']
        passage_list = filtered_response['passages']
        text_list = filtered_response['text'][:1000]

        print(passage_list[0]['passage_score'])

        def format_message(passage_list, text_list):
            message = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                                "type": "plain_text",
                            "text": "here are the top 3 results",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "type": "plain_text",
                                    "text": f"confidence level = {passage_list[0]['passage_score']}",
                                    "emoji": True
                                }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "plain_text",
                            "text": f"{passage_list[0]['passage_text']}",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "type": "plain_text",
                                    "text": f"confidence level = {passage_list[1]['passage_score']}",
                                    "emoji": True
                                }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "plain_text",
                            "text": f"{passage_list[1]['passage_text']}",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "type": "plain_text",
                                    "text": f"confidence level = {passage_list[2]['passage_score']}",
                                    "emoji": True
                                }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "plain_text",
                            "text": f"{passage_list[2]['passage_text']}",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                                "type": "plain_text",
                            "text": "expanded",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "type": "plain_text",
                                    "text": f"confidence level = {text_list[0]['confidence']}",
                                    "emoji": True
                                }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "plain_text",
                            "text": f"{text_list[0]['text'][:1000]} ...",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "type": "plain_text",
                                    "text": f"confidence level = {text_list[1]['confidence']}",
                                    "emoji": True
                                }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "plain_text",
                            "text": f"{text_list[1]['text'][:1000]} ...",
                                    "emoji": True
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                                {
                                    "type": "plain_text",
                                    "text": f"confidence level = {text_list[2]['confidence']}",
                                    "emoji": True
                                }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                                "type": "plain_text",
                            "text": f"{text_list[2]['text'][:1000]} ...",
                                    "emoji": True
                        }
                    },
                ]
            }
            return message

        message = format_message(passage_list, text_list)
        requests.post(content_response_url, json=message)
    except:
        basic_response = response['output']['generic'][0]['text']
        basic_slack_message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"{basic_response}",
                        "emoji": True
                    }
                }
            ]
        }
        requests.post(content_response_url, json=basic_slack_message)
