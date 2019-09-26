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
    driver.get("https://www.miranchitorestaurants.com/Home")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.rp-directions-location')
    for store in stores:
        location_name = store.find_element_by_css_selector('h1.rp-directions-location-name').text
        print(location_name)
        street_addr = store.find_element_by_css_selector('div:nth-child(2)').text
        state_city_zip = store.find_element_by_css_selector('div:nth-child(3)').text
        city = state_city_zip.split(',')[0]
        zipcode = state_city_zip.split(',')[1].split(' ')[-1]
        state = state_city_zip.split(',')[1].split(' ')[-2]
        phone = store.find_element_by_css_selector('div:nth-child(4)').text
        hours_of_op =  driver.find_element_by_css_selector('div.rp-hours-of-operation-store').text
        data.append([
             'https://www.miranchitorestaurants.com/',
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

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()