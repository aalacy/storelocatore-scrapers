import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


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
    driver.get("https://www.dashsmarket.com/locations/")
    stores = driver.find_elements_by_css_selector('li.locator-store-item')
    for store in stores:
        driver.switch_to.default_content()
        location_name = store.find_element_by_css_selector('h4.locator-store-name').text
        street_address = store.find_element_by_css_selector('span.locator-address').text
        state_city_zip = store.find_element_by_css_selector('span.locator-storeinformation').text.split('Phone')[0]
        city = state_city_zip.split(',')[0]
        state_zip = state_city_zip.split(',')[1]
        state = state_zip.split(" ")[1]
        zipcode = state_zip.split(" ")[2]
        phone = store.find_element_by_css_selector('a.locator-phonenumber').text
        store_number = store.get_attribute('data-store')
        hours_of_op = store.find_element_by_css_selector('span.locator-storehours').text
        data.append([
             'https://www.dashsmarket.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              store_number,
              phone,
              '<MISSING>',
              '<INACCESSIBLE>',
              '<INACCESSIBLE>',
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()