from sgselenium import SgChrome
from selenium.webdriver.chrome.options import Options
import json
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
display = Display(visible=1)
display.start()

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "lang": "en",
    "origin": "https://kuwait.pizzahut.me",
    "referer": "https://kuwait.pizzahut.me/",
    "client": "eb0b3aa0-4ab7-4c9b-8ef0-bc54bea84ca5",
    "if-none-match": 'W/"c67-RfvFOzR4Li2deW0/nRL5kFgbo0I"',
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://kuwait.pizzahut.me"
base_url = "/v2/product-hut-fe/localization/getListArea"

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--start-maximized")

with SgChrome("/home/hello/Downloads/chromedriver", is_headless=False) as driver:
    driver.get(locator_domain)
    takeaway = driver.find_element_by_css_selector('div[data-item-id="localisation-takeaway"]')
    driver.execute_script("arguments[0].click();", takeaway)
    time.sleep(1)

    driver.find_element_by_css_selector('input.input-localization').send_keys(' ')
    time.sleep(1)
    menus = driver.find_elements_by_css_selector('div.contain-outlet ul.list-outlets li')
    index = 0
    while True:
        menu = menus[index]
        try:
            driver.execute_script("arguments[0].click();", menu)
            time.sleep(1)
            rr = driver.wait_for_request('/v1/product-hut-fe/area/')
            print(rr.headers)
            items = json.loads(rr.response.body)['data']['items']
            print(len(items))
            button = driver.find_element_by_css_selector('div.contain-outlet a button')
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
            driver.find_element_by_css_selector('input.input-localization').send_keys(' ')
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.contain-outlet ul.list-outlets.aaa li",
                    )
                )
            )
            menus = driver.find_elements_by_css_selector('div.contain-outlet ul.list-outlets.aaa li')
            print(f'[index {index}] menus {len(menus)}')
            index += 1
        except Exception as err:
            print(err)
            import pdb; pdb.set_trace()
