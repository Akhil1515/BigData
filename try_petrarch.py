import json
from pprint import pprint

import requests

headers = {'Content-Type': 'application/json'}

if __name__ == '__main__':
    data = {'text': "Taliban members attacked a police vehicle in Afghanistan is Sangin (District) killing three officers. The perpetrators seized the vehicle after the attack as well. Qari Yusuf Ahmadi, Taliban spokesman, claimed responsibility for the attack via a call to AFP.",
            'id': 'eventid_1',
            'date': '20191212'
            }
    data = json.dumps(data)
    response = requests.get('http://localhost:5002/hypnos/extract', data=data, headers=headers)
    response_data = response.json()
    pprint(response_data)
