import os
import json
import re
from flask import Flask, request, jsonify
import requests
import threading
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

app = Flask(__name__)


@app.route('/', methods=['POST'])
def validation():
    message = request.get_json()['message']

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
        results_list = filtered_response['results']

        def format_for_react(n):
            try:
                score = n['passage_score']
            except KeyError:
                score = n['result_metadata']['confidence']
            try:
                text = n['passage_text']
            except KeyError:
                react_text_element_open = "<Text style={{fontWeight:'bold'}}>"
                react_text_element_close = "</Text>"
                text = n['highlight']['text'][0]
                text = text.replace("<em>", react_text_element_open)
                text = text.replace("</em>", react_text_element_close)
            response_object = {
                'confidence_score': score,
                'text': text
            }
            return response_object

        full_response = []
        for passage in passage_list:
            full_response.append(format_for_react(passage))
        for result in results_list:
            full_response.append(format_for_react(result))

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
