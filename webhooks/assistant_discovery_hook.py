import json
from watson_developer_cloud import DiscoveryV1 


def main (params):
    discovery = DiscoveryV1(
    version= "2019-04-30",
    iam_apikey = params['DISCOVERY_IAM_API_KEY']
    )
    
    context = {
        '1002': 'extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"|extracted_metadata.filename::"AU9_Victoria_Concert_Hall.pdf"|extracted_metadata.filename::"AU_5.pdf"|extracted_metadata.filename::"presence_of_the_past_the_legal_protection_of_singapores_archaeological_heritage.pdf"',
        '1003': 'extracted_metadata.filename::"project_muse_13073-396242.pdf"|extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"',
        '1004': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
        '1005': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
        '1006': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"',
    
    }

    try:
        item_index = params['item_index']
        filter = context[item_index]
        print(params['item_index'])
        
        
    except (KeyError, NameError) as error:
        filter = None
    
    query_response = discovery.query(
                        environment_id=params["DISCOVERY_ENVIRONMENT_ID"], 
                        collection_id =params["DISCOVERY_COLLECTION_ID"], 
                        filter=filter, 
                        query=None, 
                        natural_language_query=params['assistant_message'], 
                        count=3, 
                        highlight=True,
                        return_='passages, results',
                        passages='true',
                        passages_count=3,
                        passages_fields='text'
    )
    
    print(params['assistant_message'])
    print(params)
    

    data = query_response.get_result()



    return data