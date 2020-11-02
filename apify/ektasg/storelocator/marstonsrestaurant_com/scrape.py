import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('marstonsrestaurant_com')




options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
        # Your scraper here
        count=0
        data=[]
        driver.get("https://marstonsrestaurant.com/locations/")
        time.sleep(10)
        store = driver.find_element_by_css_selector('div.spb-column-inner.row.clearfix')
        location_name= store.find_element_by_css_selector('section:nth-child(1) > div > div > h3').text
        info = store.find_element_by_css_selector('section:nth-child(1) > div > div > p').text.splitlines()
        phone = info[-1]
        state_city_zip =  info[-2]
        zipcode = state_city_zip.split(" ")[-1]
        state = state_city_zip.split(" ")[-2]
        city = state_city_zip.split(",")[0]
        street_addr = info[-3]
        hours_of_op = store.find_element_by_css_selector('section:nth-child(3)').text
        data.append([
                'https://marstonsrestaurant.com/',
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                '<MISSING>',
                '<MISSING>',
                hours_of_op
            ])
        count = count + 1
        logger.info(count)

        time.sleep(3)
        driver.quit()
        return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()