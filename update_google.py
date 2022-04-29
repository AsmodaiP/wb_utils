import json
from google.oauth2 import service_account
import os
from googleapiclient.discovery import build
import datetime as dt
from dotenv import load_dotenv
import logging
import telegram


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

ID_FOR_NOTIFICATION = 295481377
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials_service.json')
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
START_POSITION_FOR_PLACE = 15
dotenv_path = os.path.join(BASE_DIR, '.env')

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1m_IcullUpEP4yOOnOH7ojBzbPpn38tFtVNyS40yKJjQ')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv('~/wb_fbs/.env ')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_end_begining(day, month, year=2022):
    current_day = day
    return (f'{year}-{month}-{current_day}T23:59:59+03:00',
            f'{year}-{month}-{current_day}T00:00:00.00+03:00')

def convert_to_column_letter(column_number):
    column_letter = ''
    while column_number != 0:
        c = ((column_number - 1) % 26)
        column_letter = chr(c + 65) + column_letter
        column_number = (column_number - c) // 26
    return column_letter

def update_table(table_id=SPREADSHEET_ID, article=0, new_price=0, user_id=0):
    range_name = 'Изменения цены'
    range_name_of_month = dt.datetime.now().strftime('%m.%Y')

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=table_id,
                                range=range_name, majorDimension='ROWS').execute()
                    

    values = result.get('values', [])
    i = 3
    body_data = []
    result = ''
    if not values:
        logging.info('No data found.')
    else:
        count = len(values)+1
        body_data = [{'range': f'{range_name}!{convert_to_column_letter(1)}{count}', 'values': [[article]]},
                    {'range': f'{range_name}!{convert_to_column_letter(2)}{count}', 'values': [[new_price]]},
                    {'range': f'{range_name}!{convert_to_column_letter(3)}{count}', 'values': [[user_id]]},
                    {'range': f'{range_name}!{convert_to_column_letter(4)}{count}', 'values': [[str(dt.datetime.now().date())]]},
                    {'range': f'{range_name}!{convert_to_column_letter(5)}{count}', 'values': [[str(dt.datetime.now().time())]]},
        ]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': body_data}

    result = sheet.values().get(spreadsheetId=table_id,
                                range=range_name_of_month, majorDimension='ROWS').execute()
    values = result.get('values', [])
    i = 1
    position_for_place = START_POSITION_FOR_PLACE + (int(dt.datetime.now().day) - 1) * 6 + 4
    for row in values:
        try:
            article_from_table = int(row[7])
            if article_from_table == article:
                body_data += [{'range': f'{range_name_of_month}!{convert_to_column_letter(position_for_place)}{i}', 'values': [[f'{new_price}{user_id.split(" ")[0]}']]}]

        except Exception as e:
            logging.error('Ошибка', e, exc_info=True)
        finally:
            i+=1

    sheet.values().batchUpdate(spreadsheetId=table_id, body=body).execute()



if __name__ == '__main__':
    pass