import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('speedyqmarkets_com')




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
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon

def parse_geo2(url):
        a = re.findall(r'\&center=(-?[\d\.]*,(--?[\d\.]*))', url)[0]
        lat = a[0].split("%2C")[0]
        lon = a[0].split("%2C")[1]
        return lat, lon

def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://www.speedyqmarkets.com/find-a-speedyq-market/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('#wpsl-stores > ul > li')
    for store in stores:
            store_id = store.get_attribute('data-store-id')
            location_name =  store.find_element_by_css_selector('div.wpsl-store-location > p > strong').text
            logger.info(location_name)
            street_addr = store.find_element_by_css_selector('span.wpsl-street').text
            state_city = store.find_element_by_css_selector('div.wpsl-store-location > p > span:nth-child(3)').text
            logger.info(state_city)
            city = state_city.split(' ')[:-1]
            citystr=''
            for i in range(0,len(city)):
                citystr = citystr + city[i]
            logger.info(citystr)
            state = state_city.split(' ')[-1]
            data.append([
             'http://www.speedyqmarkets.com/',
              location_name,
              street_addr,
              citystr,
              state,
              '<MISSING>',
              'US',
              store_id,
              '<MISSING>',
              '<MISSING>',
              '<MISSING>',
              '<MISSING>',
              '<MISSING>'
            ])


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
