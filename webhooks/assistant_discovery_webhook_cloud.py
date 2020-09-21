import json
from watson_developer_cloud import DiscoveryV1 


def main (params):
    discovery = DiscoveryV1(
    version= "2019-04-30",
    iam_apikey = params['DISCOVERY_IAM_API_KEY']
    )
    
    context = {
        '1002': 'archaeology',
        'malay_annals': '"Malay Annals"',
        'archaeology' : 'archaeology',
        }

    try:
        item_index = params['item_index']
        keyword = context[item_index]
        discovery_query_formatted = f"enriched_text.concepts.text:{keyword}"    
        print(params['item_index'])
        print(keyword) 
        print(discovery_query_formatted)
        
        
    except (KeyError, NameError) as error:
        discovery_query_formatted = None
    
    query_response = discovery.query(
                        environment_id=params["DISCOVERY_ENVIRONMENT_ID"], 
                        collection_id =params["DISCOVERY_COLLECTION_ID"], 
                        filter=discovery_query_formatted, 
                        query=None, 
                        natural_language_query=params['assistant_message'], 
                        count=3, 
                        highlight=True,
                        return_='title, subtitle',
                        passages='true',
                        passages_count=3,
                        passages_fields='text,title,subtitle'
    )
    
    print(params['assistant_message'])
    print(params)
    

    data = query_response.get_result()



    return data