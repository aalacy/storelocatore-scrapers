import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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


def fetch_data():
    # Your scraper here
    data = []
    driver.get("https://www.leesdeli.com/locations")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.txtNew')
    for store in stores:
        try:
            location_name = store.find_element_by_css_selector('h5').text
            address = store.find_element_by_css_selector('p:nth-child(2)').text
            tagged = usaddress.tag(address)[0]
            phone = store.find_element_by_css_selector('p:nth-child(3) > span').text
            hours_of_op = store.find_element_by_css_selector('p:nth-child(4) > span').text
            street_addr = location_name.split('@')[0]
            state = tagged['StateName']
            city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            data.append([
                     'https://www.leesdeli.com/',
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
        except:
            pass

    time.sleep(3)
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()