
from  parsing import get_html
from bs4 import BeautifulSoup
import json
from typing import List
from collections import namedtuple

CardInfo = namedtuple('CardInfo',('advertId', 'position', 'cpm', 'subjectId', 'brandId', 'kindId'))

def get_first_page(query):
    search_url = f'https://www.wildberries.ru/catalog/0/search.aspx?page=1&search={query}'
    
    return get_html(search_url)

def filter_adv_cards(html):
    soup = BeautifulSoup(html, 'lxml')
    cards = soup.find_all('div', class_='advert-card-item')
    return cards

def get_data_from_cards(cards: BeautifulSoup) -> List[CardInfo]:
    info = []
    for card in cards:
        info.append(CardInfo(**json.loads(card.get('data-adv-stat-fields'))))
    return info

def get_info_by_query(query):
    page = get_first_page('Брюки палаццо')
    cards= filter_adv_cards(page)
    return get_data_from_cards(cards)

if __name__ == '__main__':
    page = get_first_page('Брюки палаццо')
    cards= filter_adv_cards(page)
    print(get_data_from_cards(cards))
