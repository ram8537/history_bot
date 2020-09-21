import os
import json, re
from flask import Flask, request, jsonify
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

    if request.form.get('api_app_id') != os.environ['SLACK_APP_ID']:
        return "looks like you got the wrong bot pal!", 400

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

@app.route('/detail-view', methods=['POST'])
def detail_view():

    items = {
        '1001' : { 
        'title': "Abraham Ortelius's map of Southeast Asia",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/map.jpg',
        'description': "Abraham Ortelius (1527-1598) was a Flemish cartographer whose Theatrum Orbis Terrarum (Theatre of the World) was regarded as the first modern atlas. In this 1570 map, the Malay Peninsula appears as an elongated extension of mainland Southeast Asia, and Singapore as an appendix, marked 'Cincapura', with a cluster of islets. As was common practice for the time, the map also has illustrations of mermaids and imaginary sea creatures.", 
        },
        '1002' : { 
        'title': "Archaeology",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1002_arch.jpg',
        'description': "Although there are only a few historical sources that address Singapore's pre-colonial past, archaeology has helped to fill some of the gaps. Since 1984, archaeologists in Singapore have uncovered traces of pre-colonial Singapura or Temasek in the Singapore River and Fort Canning areas. This settlement flourished for about a hundred years between the 14th and 15 centuries. This was followed by a hiatus in the 165h century, before a brief revival in the 17th century. Over the years, archaeological excavations have revealed many remarkable finds. Some highlights which were recovered from 2001 to 2015 are displayed here. All objects in this showcase are courtesy of the Archaeology Unit, Institute of Southeast Asian Studies.",
        },
        '1003' : { 
        'title': "Singapore Stone",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1003_stone.jpg',
        'description': "10-14th centuries, Singapore River mouth, Inscribed sandstone.", 
        },
        '1004' : { 
        'title': "Singapura 1299-1818",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1004_statue_sangnilaautama.jpg',
        'description': "Where does Singapore's history begin?",
        },
    }

        
    def format(item_number, title, image_url, description):
        formatted_response = {
            "blocks": [
                {
                    "type": "divider"
                },
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{item_number}:{title}",
                        "emoji": True
                    }
                },
                {
                    "type": "image",
                    "image_url": f"{image_url}",
                    "alt_text": "inspiration"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"{description}",
                        "emoji": True
                    }
                }
            ]
        }
    
        return formatted_response

    try:
        slack_user_input = request.form.get('text')
        print(slack_user_input)
        match = re.match("1\d{3}", slack_user_input)
        if match:
            item_to_search = match.group()
            search = items[item_to_search]
            response_message = format(item_to_search, search['title'], search['image_url'],search['description'])
        else:
            print('no match')
    except KeyError:
        pass

    print(request.form)
    try:
        return jsonify(response_message), 200
    except:
        return jsonify("Sorry but I could not find anything"), 200
    
