import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from selenium.common.exceptions import StaleElementReferenceException
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('landismarket_com')



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
    driver.get("https://www.landismarket.com/store-locations/")
    stores = driver.find_elements_by_css_selector('div.panel.panel-success.panel-location')
    for store in stores:
        try:
            location_name = store.find_element_by_css_selector('div.panel-heading > h2').text
        except StaleElementReferenceException as Exception:
            logger.info('StaleElementReferenceException while trying to location_name, trying to find element again')
            location_name = store.find_element_by_css_selector('div.panel-heading > h2').text
        try:
            raw_address = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7 > p:nth-child(2)').text
        except StaleElementReferenceException as Exception:
            logger.info('StaleElementReferenceException while trying to raw_address, trying to find element again')
            raw_address = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7 > p:nth-child(2)').text
        tagged = usaddress.tag(raw_address)[0]
        try:
            street_addr = tagged['BuildingName'].split('\n')[0] + " " + tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        except:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        state = tagged['StateName']
        city = tagged['PlaceName']
        zipcode = tagged['ZipCode']
        try:
            phone = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7 > a').text
        except StaleElementReferenceException as Exception:
            logger.info('StaleElementReferenceException while trying to phone, trying to find element again')
            phone = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7 > a').text
        #driver.implicitly_wait(20)
        try:
            geomap = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7 > p:nth-child(3) > a').get_attribute('href')
        except StaleElementReferenceException as Exception:
            logger.info('StaleElementReferenceException while trying to geomap, trying to find element again')
            geomap = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7 > p:nth-child(3) > a').get_attribute(
                'href')
        lat, lon = parse_geo(geomap)
        try:
            hours_of_op = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7').text.split('Hours:')[1]
        except StaleElementReferenceException as Exception:
            logger.info('StaleElementReferenceException while trying to hours of op, trying to find element again')
            hours_of_op = store.find_element_by_css_selector('div.panel-body > div.col-xs-12.col-sm-6.col-sm-push-6.col-md-7.col-md-push-5 > div > div.col-md-7').text.split('Hours:')[1]
        data.append([
             'https://www.landismarket.com/',
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
              lon,
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()