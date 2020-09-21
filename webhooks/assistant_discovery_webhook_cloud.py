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
        '1002': 'extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"|extracted_metadata.filename::"AU9_Victoria_Concert_Hall.pdf"|extracted_metadata.filename::"AU_5.pdf"|extracted_metadata.filename::"presence_of_the_past_the_legal_protection_of_singapores_archaeological_heritage.pdf"',
        '1003': 'extracted_metadata.filename::"project_muse_13073-396242.pdf"|extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"',
        '1004': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
        '1005': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
        '1006': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"',

    }


    try:
        item_index = request.form.get('item_index')
        filter = context[item_index]
        print(request.form.get('item_index'])
        print(keyword) 
        
        
    except (KeyError, NameError) as error:
        discovery_query_formatted = None


    query_response = discovery.query(
                        environment_id=os.environ["WATSON_DISCOVERY_ENVIRONMENT_ID"],  
                        collection_id =os.environ["WATSON_DISCOVERY_COLLECTION_ID"], 
                        filter=filter, 
                        query=None, 
                        natural_language_query=request.form.get('assistant_message'), 
                        count=3, 
                        highlight=True,
                        return_='title, subtitle',
                        passages='true',
                        passages_count=3,
                        passages_fields='text'
    )
    
    print(request.form.get('assistant_message'))
    print(request.form)

    data = query_response.get_result()
    return jsonify(data), 200
    
 
   


