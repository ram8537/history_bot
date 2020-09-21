import os
import json
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
    '1002': 'extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"|extracted_metadata.filename::"AU9_Victoria_Concert_Hall.pdf"|extracted_metadata.filename::"AU_5.pdf"|extracted_metadata.filename::"presence_of_the_past_the_legal_protection_of_singapores_archaeological_heritage.pdf"',
    '1003': 'extracted_metadata.filename::"project_muse_13073-396242.pdf"|extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"',
    '1004': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
    '1005': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"',
    '1006': 'extracted_metadata.filename::"project_muse_13073-396241.pdf"|extracted_metadata.filename::"Singapore and its Straits c 1500 1800.pdf"|extracted_metadata.filename::"Full_book_miksic_part_1.pdf"|extracted_metadata.filename::"Full_book_miksic_part_2.pdf"|extracted_metadata.filename::"Pages from 2017_Book_HandbookOfEastAndSoutheastAsia.pdf"',

}

##for testing only:
params = {
    'item_index' : '1005'
}

try:
    item_index = params['item_index']
    keyword = context[item_index]
    discovery_query_formatted = f"enriched_text.concepts.text:{keyword}"
except (KeyError, NameError) as error:
    discovery_query_formatted = None

question = 'singapore stone'

try:

    query_response = discovery.query(environment_id=os.environ["WATSON_DISCOVERY_ENVIRONMENT_ID"],
                                     collection_id=os.environ["WATSON_DISCOVERY_COLLECTION_ID"],
                                     filter=context['1002'],
                                     natural_language_query= question,
                                     return_='passages, results',
                                     passages=True,
                                     passages_count=3,
                                     passages_fields='text',
                                     highlight=True
                                     )

    data = query_response.get_result()

    print(data)


except ApiException as ex:

    print("Method failed with status code " + str(ex.code) + ": " + ex.message)
