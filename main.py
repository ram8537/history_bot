import os
import json, re
import threading
from flask import Flask, request, jsonify
import requests
from ibm_watson import AssistantV2
from ibm_watson import DiscoveryV1
from ibm_watson import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

app = Flask(__name__)


@app.route('/', methods=['POST'])
def react():
    message = str(request.get_json()['message'])

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

    try:
        list_of_responses = []
        print("sending filtered message")
        filtered_response = response['output']['user_defined']['personal_api']['watson_response']
        passage_list = filtered_response['passages']

        def format_for_react(n):
            score = n['passage_score']
            text = n['passage_text']
            response_object = {
                'confidence_score': score,
                'text': text
            }
            return response_object

        full_response = [format_for_react(passage) for passage in passage_list]

        reply = {
            'type': 'filtered_response',
            'message': full_response
        }
        return jsonify(reply), 200

    except KeyError:
        try:
            print("sending prepared response")
            basic_response = response['output']['generic'][0]['text']
            reply = {
                'type': 'basic_response',
                'message': basic_response
            }
            return jsonify(reply), 200

        except IndexError:
            print("caught at intent")
            message = "caught at intent"
            reply = {
                'type': 'error_response',
                'message': message
            }
            return jsonify(reply), 200


@app.route('/assistant-discovery', methods=['POST'])
def assistant_discovery():
    assistant_payload = request.get_json()
    message = assistant_payload['assistant_message']

    print(assistant_payload)

    authenticator = IAMAuthenticator(os.environ["WATSON_DISCOVERY_API_KEY"])
    discovery = DiscoveryV1(
        version='2020-04-01',
        authenticator=authenticator
    )
    discovery.set_service_url(os.environ["WATSON_DISCOVERY_URL"])

    context = {
        '1002': 'extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"|extracted_metadata.filename::"AU9_Victoria_Concert_Hall.pdf"|extracted_metadata.filename::"AU_5.pdf"|extracted_metadata.filename::"presence_of_the_past_the_legal_protection_of_singapores_archaeological_heritage.pdf"',
        '1003': 'extracted_metadata.filename::"project_muse_13073-396242.pdf"|extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"',
        '1004': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
        '1005': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
        '1006': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"',

    }

    try:
        item_index = assistant_payload['item_index']
        filter = context[item_index]
        discovery_query_formatted = f"enriched_text.concepts.text:{keyword}"

    except (KeyError, NameError) as error:
        filter = None

    try:
        query_response = discovery.query(environment_id=os.environ["WATSON_DISCOVERY_ENVIRONMENT_ID"],
                                         collection_id=os.environ["WATSON_DISCOVERY_COLLECTION_ID"],
                                         filter=filter,
                                         natural_language_query=message,
                                         return_='id,extracted_metadata.title, result_metadata',
                                         passages=True,
                                         passages_count=5,
                                         count=3,
                                         )

        data = query_response.get_result()
        return data

    except ApiException as ex:
        print("Method failed with status code " +
              str(ex.code) + ": " + ex.message)

@app.route('/slack', methods=['POST'])
def slack_deprecated():
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
        filtered_response = response['output']['user_defined']['personal_api']['watson_response']
        print(filtered_response)
        passage_list = filtered_response['passages']
        results_list = filtered_response['results']
        
        def slack_formatter_score(n):
            try:
                score = n['passage_score']
            except KeyError:
                score = n['result_metadata']['confidence']
            slack_component_score = {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": f"confidence level = {score}",
                    }
                ]
            }
            return slack_component_score

        def slack_formatter_text(n):
            try:
                text = n['passage_text']
            except KeyError:
                text = n['highlight']['text'][0]
                text = text.replace("<em>", "_*")
                text = text.replace("</em>", "*_")
            slack_component_text = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{text}",
                }
            }
            return slack_component_text

        header_1 = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "here are the top 3 results"
            }
        }
        divider = {
            "type": "divider"
        }

        header_2 = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "expanded"
            }
        }
        formatted_passages_score = [slack_formatter_score(passage) for passage in passage_list]
        formatted_passages_text = [slack_formatter_text(passage) for passage in passage_list]
        formatted_text_score = [slack_formatter_score(result) for result in results_list ]
        formatted_text_text = [slack_formatter_text(result) for result in results_list ]


        ##combine everything
        final_components_list = []
        final_components_list.append(header_1)
        for i in range (len(formatted_passages_score)):
            final_components_list.append(formatted_passages_score[i])
            final_components_list.append(formatted_passages_text[i])

        final_components_list.append(divider)
        final_components_list.append(header_2)

        for i in range (len(formatted_text_score)):
            final_components_list.append(formatted_text_score[i])
            final_components_list.append(formatted_text_text[i])


        slack_message = {
            'blocks' : final_components_list
        } 
        print("slack_message")
        print(slack_message)

        requests.post(content_response_url, json=slack_message)
    
    except:
        print("sending basic response")
        try:
            basic_response = response['output']['generic'][0]['text']
            basic_slack_message = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f"{basic_response}",
                       
                        }
                    }
                ]
            }
            requests.post(content_response_url, json=basic_slack_message)
        except IndexError:
            basic_slack_message = {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f"(caught at intent)",
                       
                        }
                    }
                ]
            }
            requests.post(content_response_url, json=basic_slack_message)


@ app.route('/slack/detail-view', methods=['POST'])
def slack_detail_view_deprecated():
    items = {
        '1001': {
            'title': "Abraham Ortelius's map of Southeast Asia",
            'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/map.jpg',
            'description': "Abraham Ortelius (1527-1598) was a Flemish cartographer whose Theatrum Orbis Terrarum (Theatre of the World) was regarded as the first modern atlas. In this 1570 map, the Malay Peninsula appears as an elongated extension of mainland Southeast Asia, and Singapore as an appendix, marked 'Cincapura', with a cluster of islets. As was common practice for the time, the map also has illustrations of mermaids and imaginary sea creatures.",
        },
        '1002': {
            'title': "Archaeology",
            'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1002_arch.jpg',
            'description': "Although there are only a few historical sources that address Singapore's pre-colonial past, archaeology has helped to fill some of the gaps. Since 1984, archaeologists in Singapore have uncovered traces of pre-colonial Singapura or Temasek in the Singapore River and Fort Canning areas. This settlement flourished for about a hundred years between the 14th and 15 centuries. This was followed by a hiatus in the 165h century, before a brief revival in the 17th century. Over the years, archaeological excavations have revealed many remarkable finds. Some highlights which were recovered from 2001 to 2015 are displayed here. All objects in this showcase are courtesy of the Archaeology Unit, Institute of Southeast Asian Studies.",
        },
        '1003': {
            'title': "Singapore Stone",
            'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1003_stone.jpg',
            'description': "10-14th centuries, Singapore River mouth, Inscribed sandstone.",
        },
        '1004': {
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
            response_message = format(
                item_to_search, search['title'], search['image_url'], search['description'])
        else:
            print('no match')
    except KeyError:
        pass

    try:
        return jsonify(response_message), 200
    except:
        return jsonify("Sorry but I could not find anything"), 200