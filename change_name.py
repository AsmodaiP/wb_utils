from hashlib import new
from lib2to3.pgen2 import token
import requests


from dotenv import load_dotenv
import os
import json

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_file = os.path.join(BASE_DIR, 'credentials.json')

base_url_for_getting_orders = 'https://suppliers-api.wildberries.ru/api/v2/orders'
TOKEN = os.environ.get('TOKEN')

CRED = json.load(open(os.path.join(BASE_DIR,'credentials.json'), 'rb'))

def get_card_by_imtID(imtID):
    for name in CRED.keys():
        token = CRED[name]['token']

        headers = {
            'Authorization': token,
        }
        url = 'https://suppliers-api.wildberries.ru/card/cardByImtID'
        data={
            "id": 1,
            "jsonrpc": "2.0",
            "params": {
                "imtID": imtID,
                "supplierID": "19db61da-bb18-545e-894e-4afcc23879f5"
        }}
        response = requests.post(url, headers=headers, json=data)
        if 'result' in response.json():
            return response.json()['result']['card']


def update_card(card, new_name):
    url = 'https://suppliers-api.wildberries.ru//card/update'

    for param in card['addin']:
        if param['type']=='Наименование':
            param['params'][0]['value']=new_name

    for name in CRED.keys():
        token = CRED[name]['token']
        headers = {
            'Authorization': token,
        }
        data = {
        "id": 1,
        "jsonrpc": "2.0",
        "params": {
            "card":  card
            }
        }
        with open('sdf.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        response = requests.post(url, headers=headers, json = data)
        if 'error' in response.json():
            if  'failed get card' in response.json()['error']['data']['err']:
                continue
        return (response.json())

def update_card_by_imtID(imtID, new_name):
    print(new_name, imtID)
    # try:
    card = get_card_by_imtID(int(imtID))
    print(card)
    # except:
    #     return f'Не удалось получить карточку по imtID={imtID}'
    return update_card(card, new_name)



print(update_card_by_imtID(26161227, 'Костюм женский спортивный / с шортами / летний / оверсайз /с велосипедками/домашний'))