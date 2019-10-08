import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress


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
    a=re.findall(r'\?ll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def parse_geo2(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://www.phoenixfood.us/locations")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.locations-item')
    for store in stores:
        location_name = store.find_element_by_css_selector('p').text
        raw_address = store.find_element_by_css_selector('div.locations-info > p:nth-child(1)').text.split('Address:')[1]
        street_addr = raw_address.split(',')[0]
        city = raw_address.split(',')[1]
        state_zip = raw_address.split(',')[2]
        state = state_zip.split(' ')[-2]
        zipcode = state_zip.split(' ')[-1]
        phone = store.find_element_by_xpath("//a[contains(@href,'tel:')]").text
        geomap = store.find_element_by_css_selector('a.locations-item-link').get_attribute('onClick')
        try:
            lat,lon = parse_geo(geomap)
        except:
            lat,lon = parse_geo2(geomap)
        loc_type = store.find_element_by_css_selector('a.locations-item-link').text
        hours_of_op = store.find_element_by_css_selector('div.locations-info > p:nth-child(3)').text
        data.append([
             'http://www.phoenixfood.us/',
              location_name,
              street_addr,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              loc_type,
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