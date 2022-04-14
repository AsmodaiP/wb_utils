from selenium.webdriver.firefox.options import Options
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from cookie import COOKIE
from bs4 import BeautifulSoup
import time

headers = {
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_html(url):
    options = Options()
    options.headless = True
    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = "eager"

    firefoxProfile = webdriver.FirefoxProfile()
    firefoxProfile.set_preference('permissions.default.stylesheet', 2)
    firefoxProfile.set_preference('permissions.default.image', 2)
    firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
    firefoxProfile.set_preference("http.response.timeout", 10)
    firefoxProfile.set_preference("dom.max_script_run_time", 10)

    driver = webdriver.Firefox(options=options, desired_capabilities=caps, firefox_profile=firefoxProfile)
    driver.get('https://www.wildberries.ru/')
    
    try:
        driver.set_window_size(1920, 1080)
        driver.set_page_load_timeout(30)

        driver.get(url)
        driver.delete_cookie('__wbl')
        for coc in COOKIE['spb']:
            coc['sameSite'] = 'Strict'
            
            driver.add_cookie(coc)
        driver.get(url)
        # time.sleep(333)
        # with open('coockit.json')
        # print(driver.get_cookies())
        SCROLL_PAUSE_TIME = 4
    
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(20):
            # Scroll down to bottom
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
    except Exception as e:
        driver.close()
        time.sleep(10)
        raise e
    driver.close()
    return html