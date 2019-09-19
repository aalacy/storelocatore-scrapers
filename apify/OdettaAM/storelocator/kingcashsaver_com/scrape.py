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
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://kingcashsaver.com/stores.php")
    time.sleep(10)
    stores1 = driver.find_elements_by_css_selector('body > div:nth-child(3) > div.container > div:nth-child(1) > div > div:nth-child(2) > p')
    stores2 = driver.find_elements_by_css_selector('body > div:nth-child(3) > div.container > div:nth-child(1) > div > div:nth-child(3) > p')
    stores = stores1 + stores2
    for store in stores:
        address = store.find_element_by_css_selector('a').text
        tagged = usaddress.tag(address)[0]
        try:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName']
        except:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
        state = tagged['StateName']
        city = tagged['PlaceName']
        info = store.text
        phone = info.split('\n')[1]
        geomap = store.find_element_by_css_selector('a').get_attribute('href')
        lat,lon = parse_geo(geomap)
        hours_of_op = info.split('Store Hours:')[1]
        data.append([
             'http://kingcashsaver.com/',
              '<MISSING>',
              street_addr,
              city,
              state,
              '<MISSING>',
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