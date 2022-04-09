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

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', None)
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

def update_table(table_id='1m_IcullUpEP4yOOnOH7ojBzbPpn38tFtVNyS40yKJjQ', article=0, new_price=0, user_id=0):
    range_name = 'Изменения цены'

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
        print(body)
        sheet.values().batchUpdate(spreadsheetId=table_id, body=body).execute()



if __name__ == '__main__':
    
    cred_file = os.path.join(BASE_DIR, 'credentials.json')   
    with open(cred_file, 'r') as fp:
        cred = json.load(fp)
        table_id ='
        day = dt.datetime.now().day 
        month = dt.datetime.now().month
        update_table( table_id, 17290081, '222', 'user_id')
