import json
from watson_developer_cloud import DiscoveryV1 

@app.route('/assistant-discovery', methods=['POST'])
def main ():
    authenticator = IAMAuthenticator(os.environ["WATSON_DISCOVERY_API_KEY"])
    discovery = DiscoveryV1(
    version='2020-04-01',
    authenticator=authenticator
    )

    discovery.set_service_url(os.environ["WATSON_DISCOVERY_URL"])

    
    context = {
        '1002': 'archaeology',
        'malay_annals': '"Malay Annals"',
        'archaeology' : 'archaeology',
        }

    try:
        item_index = request.form.get('item_index')
        keyword = context[item_index]
        discovery_query_formatted = f"enriched_text.concepts.text:{keyword}"    
        print(request.form.get('item_index'])
        print(keyword) 
        print(discovery_query_formatted)
        
        
    except (KeyError, NameError) as error:
        discovery_query_formatted = None


    query_response = discovery.query(
                        environment_id=os.environ["WATSON_DISCOVERY_ENVIRONMENT_ID"],  
                        collection_id =os.environ["WATSON_DISCOVERY_COLLECTION_ID"], 
                        filter=discovery_query_formatted, 
                        query=None, 
                        natural_language_query=request.form.get('assistant_message'), 
                        count=3, 
                        highlight=True,
                        return_='title, subtitle',
                        passages='true',
                        passages_count=3,
                        passages_fields='text,title,subtitle'
    )
    
    print(request.form.get('assistant_message'))
    print(request.form)

    data = query_response.get_result()
    return jsonify(data), 200
    
 
   


