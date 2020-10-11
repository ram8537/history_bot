import os
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException, AssistantV2, DiscoveryV1
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Filters, Items, FAQ
from .serializers import ItemsSerializer, ReactFilteredResponseSerializer, FAQSerializer


class ItemsListView(ListAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer


class ItemsDetailView(RetrieveAPIView):
    queryset = Items.objects.all()
    serializer_class = ItemsSerializer


class ReactWatsonAssistant(APIView):
    queryset = User.objects.none()

    def get(self, request, format=None):
        message = request.query_params['message']
        print("(ReactWatsonAssistant) message received from React:", message)

        authenticator = IAMAuthenticator(
            os.environ['WATSON_ASSISTANT_API_KEY'])
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
            filtered_response = response['output']['user_defined']['personal_api']['watson_response']
            passage_list = filtered_response['passages']
            filtered_response_serialized = ReactFilteredResponseSerializer(
                passage_list, many=True)
            reply = {
                'type': 'filtered_response',
                'message': filtered_response_serialized.data
            }
            print("sending filtered_response")
            return Response(reply)

        except KeyError:
            try:
                basic_response = response['output']['generic'][0]['text']
                reply = {
                    'type': 'basic_response',
                    'message': basic_response
                }
                print("sending prepared response")
                return Response(reply)

            except IndexError:
                message = "sorry but there seems to be a problem"
                reply = {
                    'type': 'error_message',
                    'message': 'Sorry but there seems to be a problem'
                }
                print("sending error response/caught at intent")
                return Response(reply)


class AssistantDiscovery(APIView):
    queryset = User.objects.none()
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format=None):
        assistant_payload = request.data
        message = request.data['assistant_message']
        print("(assistant discovery hook), assistant payload:", assistant_payload)

        authenticator = IAMAuthenticator(
            os.environ["WATSON_DISCOVERY_API_KEY"])
        discovery = DiscoveryV1(
            version='2020-04-01',
            authenticator=authenticator
        )
        discovery.set_service_url(os.environ["WATSON_DISCOVERY_URL"])

        try:
            item_index = assistant_payload['item_index']
            obj = Filters.objects.get(pk=item_index)
            filter = obj.query_language_filter
            print("(assistant-discovery hook) using filter:", item_index, filter)

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
            return Response(data)

        except ApiException as ex:
            print(
                "(assistant-discovery webhook) error with watson assistant's response", ex)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response()


class FAQListView(ListAPIView):
    serializer_class = FAQSerializer
    def get_queryset(self):
        item_number = self.kwargs['item_number']
        return FAQ.objects.filter(item_number=item_number)

        
