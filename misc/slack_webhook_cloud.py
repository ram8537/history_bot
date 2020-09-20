import sys, json, re


def main(props):

    items = {
        '1001' : { 
        'title': "Abraham Ortelius's map of Southeast Asia",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/map.jpg',
        'description': "Abraham Ortelius (1527-1598) was a Flemish cartographer whose Theatrum Orbis Terrarum (Theatre of the World) was regarded as the first modern atlas. In this 1570 map, the Malay Peninsula appears as an elongated extension of mainland Southeast Asia, and Singapore as an appendix, marked 'Cincapura', with a cluster of islets. As was common practice for the time, the map also has illustrations of mermaids and imaginary sea creatures.", 
        },
        '1002' : { 
        'title': "Archaeology",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1002_arch.jpg',
        'description': "Although there are only a few historical sources that address Singapore's pre-colonial past, archaeology has helped to fill some of the gaps. Since 1984, archaeologists in Singapore have uncovered traces of pre-colonial Singapura or Temasek in the Singapore River and Fort Canning areas. This settlement flourished for about a hundred years between the 14th and 15 centuries. This was followed by a hiatus in the 165h century, before a brief revival in the 17th century. Over the years, archaeological excavations have revealed many remarkable finds. Some highlights which were recovered from 2001 to 2015 are displayed here. All objects in this showcase are courtesy of the Archaeology Unit, Institute of Southeast Asian Studies.",
        },
        '1003' : { 
        'title': "Singapore Stone",
        'image_url': 'https://cloud-object-storage-zn-cos-standard-nlt.s3.jp-tok.cloud-object-storage.appdomain.cloud/1003_stone.jpg',
        'description': "10-14th centuries, Singapore River mouth, Inscribed sandstone.", 
        },
        '1004' : { 
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
                        "emoji": True
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
                        "emoji": True
                    }
                }
            ]
        }
    
        return formatted_response


    try:
        slack__user_input = props['text']
        match = re.match("1\d{3}", slack__user_input)
        if match:
            item_to_search = match.group()
            search = items[item_to_search]
            response_message = format(item_to_search, search['title'], search['image_url'],search['description'])
        else:
            print('no match')
    except KeyError:
        pass

    try:
        response =  {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json'},
            'body': json.dumps(response_message),
        }
    except:
        response =  {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json'},
            'body': 'Sorry but I could not find anything ',
        }
        
    print(props)
        
    return response

