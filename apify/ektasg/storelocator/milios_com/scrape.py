import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('milios_com')




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
    data=[]
    driver.get("https://milios.com/stores/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.col-md-4.archive-store-item > div.image-container > a')
    names = [stores[i].get_attribute('href') for i in range(0,len(stores))]
    for i in range(0, len(names)):
        driver.get(names[i])
        time.sleep(5)
        location_name = driver.find_element_by_css_selector('div.location-info-left > h1').text
        logger.info(location_name)
        raw_address = driver.find_element_by_css_selector('div.address-locator').text
        address = raw_address.splitlines()
        street_addr = address[0]
        city = address[1].split(',')[0]
        zipcode = address[1].split(',')[1].split(' ')[-1]
        state = address[1].split(',')[1].split(' ')[-2]
        phone = address[2]
        hours_of_op =  driver.find_element_by_css_selector('div.location-info-left > div:nth-child(4) > h3').text + " " + \
                       driver.find_element_by_css_selector('div.location-info-left > div:nth-child(4) > ul').text +  " " + \
                       driver.find_element_by_css_selector('div.location-info-left > div:nth-child(5) > h3').text +  " " + \
                       driver.find_element_by_css_selector('div.location-info-left > div:nth-child(5) > ul').text
        lat = driver.execute_script("return miliosStores;")[0][1]
        lng = driver.execute_script("return miliosStores;")[0][2]
        data.append([
             'https://milios.com/',
              location_name,
              street_addr,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              lat,
              lng,
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()