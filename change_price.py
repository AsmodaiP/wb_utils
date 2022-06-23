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
        return 'Попытка изменить цену на слишком высокую'
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
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            return f'Цена изменена, новая окончательная цена {new_price*(1-current_price_info["discount"]*0.01) * (1- current_price_info["promoCode"]*0.01)} Запрос {json.dumps(json_data)}'
if __name__ == '__main__':
    print(get_info_current_price(74771522))
