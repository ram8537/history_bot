import os, json
from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException

authenticator = IAMAuthenticator(os.environ["WATSON_DISCOVERY_API_KEY"])
discovery = DiscoveryV1(
    version='2020-04-01',
    authenticator=authenticator
)

discovery.set_service_url(os.environ["WATSON_DISCOVERY_URL"])


context = {
'1002': 'archaeology',
'malay_annals': '"malay annals"'
}


try:
    item_index = params['item_index']
    keyword = context[item_index]
    discovery_query_formatted = f"enriched_text.concepts.text:{keyword}"
except (KeyError, NameError) as error:
    discovery_query_formatted = None



try:

    query_response = discovery.query(environment_id=os.environ["WATSON_DISCOVERY_ENVIRONMENT_ID"], 
                        collection_id =os.environ["WATSON_DISCOVERY_COLLECTION_ID"], 
                        filter=discovery_query_formatted, 
                        natural_language_query="sejarah when was it written", 
                        count=3, 
                        return_='title, subtitle, text',
                        passages='true',
                        passages_count=3,
                        passages_fields='text,title,subtitle'
    )
    
    data = query_response.get_result()
    
    print(data)


except ApiException as ex:
    
    print ("Method failed with status code " + str(ex.code) + ": " + ex.message)
