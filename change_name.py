from asyncio import exceptions
from hashlib import new
from lib2to3.pgen2 import token
import requests


from dotenv import load_dotenv
import os
import json

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_file = os.path.join(BASE_DIR, 'credentials.json')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CRED = json.load(open(os.path.join(BASE_DIR,'credentials.json'), 'rb'))

base_url_for_getting_orders = 'https://suppliers-api.wildberries.ru/api/v2/orders'
TOKEN = os.environ.get('TOKEN')
with open(cred_file, 'r') as fp:
        cred = json.load(fp)

def get_card_by_imtID(token, imtID):
    url = 'https://suppliers-api.wildberries.ru/card/cardByImtID'
    headers = {
        'Authorization': token,
    }
    data={
        "id": 1,
        "jsonrpc": "2.0",
        "params": {
            "imtID": imtID,
            "supplierID": "19db61da-bb18-545e-894e-4afcc23879f5"
    }}
    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    return response.json()['result']['card']

b_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6ImQyY2FkNGJjLWJmNTQtNGI3NC1hY2RmLTVmNzFhMzdlY2ZiYyJ9.23vWr2KtMPEWQcOmcyS8P7KKzRA8eCKxbd9eUFagAUs'


def update_card(token, card, new_name):
    url = 'https://suppliers-api.wildberries.ru//card/update'

    for param in card['addin']:
        if param['type']=='Наименование':
            param['params'][0]['value']=new_name
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
    return (response.json())

def update_card_by_imtID(imtID, new_name, token=b_token):
    print(new_name, imtID)
    # try:
    card = get_card_by_imtID(token, int(imtID))
    # except:
    #     return f'Не удалось получить карточку по imtID={imtID}'
    return update_card(token, card, new_name)


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
with open(cred_file, 'r') as fp:
        cred = json.load(fp)

def get_card_by_imtID(token, imtID):
    url = 'https://suppliers-api.wildberries.ru/card/cardByImtID'
    headers = {
        'Authorization': token,
    }
    data={
        "id": 1,
        "jsonrpc": "2.0",
        "params": {
            "imtID": imtID,
            "supplierID": "19db61da-bb18-545e-894e-4afcc23879f5"
    }}
    response = requests.post(url, headers=headers, json=data)
    return response.json()['result']['card']

b_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6ImQyY2FkNGJjLWJmNTQtNGI3NC1hY2RmLTVmNzFhMzdlY2ZiYyJ9.23vWr2KtMPEWQcOmcyS8P7KKzRA8eCKxbd9eUFagAUs'


def update_card(token, card, new_name):
    url = 'https://suppliers-api.wildberries.ru//card/update'

    for param in card['addin']:
        if param['type']=='Наименование':
            param['params'][0]['value']=new_name
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
    return (response.json())

def update_name_by_imtID(imtID, new_name):
    for name in CRED.keys():
        try:
            token = CRED[name]['token']
            card = get_card_by_imtID(token, int(imtID))
            result = update_card(token, card, new_name)
            return result
        except:
            pass
    return f'Не удалось получить карточку по imtID={imtID}'

