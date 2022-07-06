from cmath import inf
import requests
import json

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CRED = json.load(open(os.path.join(BASE_DIR, 'credentials.json'), 'rb'))


def get_info_current_price(article):
    for name in CRED.keys():
        token = CRED[name]['token']

        headers = {
            'Authorization': token,
        }
        url = "https://suppliers-api.wildberries.ru/public/api/v1/info"
        response = requests.get(url, headers=headers, params={'quantity': 0})
        for info in response.json():
            if info['nmId'] == article:
                info['Цена после скидок'] = int(
                    info['price'] * (1 - info['discount'] * 0.01) * (1 - info['promoCode'] * 0.01))
                return info


def validate_new_price(current_price, new_price):
    if current_price * 0.85 > new_price:
        return False
    return True


def change_price(article, new_price, chat_id):
    url = "https://suppliers-api.wildberries.ru/public/api/v1/prices"

    current_price_info = get_info_current_price(article)

    new_price = int((new_price /
                     (1 -
                      current_price_info['promoCode'] *
                      0.01)) /
                    (1 -
                     current_price_info['discount'] *
                     0.01))
    if not validate_new_price(current_price_info['price'], new_price) and chat_id != 172902983:
        return 'Попытка изменить цену на слишком низкую.'
    for name in CRED.keys():
        token = CRED[name]['token']

        headers = {
            'Authorization': token,
        }
        json_data = [
            {
                "nmId": article,
                "price": new_price
            }
        ]
        name_of_good = get_name_by_article(article)
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            return f'Цена изменена \n Имя товара {name_of_good} \n артикул {article} \nстарая цена -- {current_price_info["Цена после скидок"]} \n новая окончательная цена  -- {new_price*(1-current_price_info["discount"]*0.01) * (1- current_price_info["promoCode"]*0.01)} \n Запрос`{json.dumps(json_data)}`'


def get_name_by_article(article):
    for name in CRED.keys():
        try:
            token = CRED[name]['token']

            headers = {
                'Authorization': token,
            }
            url = 'https://suppliers-api.wildberries.ru/card/list'
            json_for_request = {
                "id": 1,
                "jsonrpc": "2.0",
                "params": {
                    "filter": {
                        "find": [
                            {
                                "column": "nomenclatures.nmId",
                                "search": article
                            }
                        ],
                        "order": {
                            "column": "string",
                            "order": "string"
                        }
                    }
                }
            }
            response = requests.post(url=url, headers=headers, json=json_for_request)
            card = response.json()['result']['cards'][0]
            addins = card['addin']
            for element in addins:
                if element['type'] == 'Наименование':
                    return element['params'][0]['value']
        except Exception as e:
            pass


def get_inside_article(article: int) -> str:
    for name in CRED.keys():
        try:
            token = CRED[name]['token']

            headers = {
                'Authorization': token,
            }
            url = 'https://suppliers-api.wildberries.ru/card/list'
            json_for_request = {
                "id": 1,
                "jsonrpc": "2.0",
                "params": {
                    "filter": {
                        "find": [
                            {
                                "column": "nomenclatures.nmId",
                                "search": article
                            }
                        ],
                        "order": {
                            "column": "string",
                            "order": "string"
                        }
                    }
                }
            }
            response = requests.post(url=url, headers=headers, json=json_for_request)
            card = response.json()['result']['cards'][0]

            return card['nomenclatures'][0]['vendorCode']
        except Exception as e:
            pass


if __name__ == '__main__':
    print(get_inside_article(34778015))
