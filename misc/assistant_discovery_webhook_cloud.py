import json
from watson_developer_cloud import DiscoveryV1


def main(params):
    discovery = DiscoveryV1(
        version="2019-04-30",
        iam_apikey=params['DISCOVERY_IAM_API_KEY']
    )

    query_response = discovery.query(
        environment_id=params["DISCOVERY_ENVIRONMENT_ID"],
        collection_id=params["DISCOVERY_COLLECTION_ID"],
        filter=None,

        query=None,
        natural_language_query="who is sang nila utama",
        count=3,
        return_='title, subtitle',
        passages='true',
        passages_count=3,
        passages_fields='text,title,subtitle'
    )

    print(params['assistant_message'])
    data = query_response.get_result()

    return data
