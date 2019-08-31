import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress
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
    driver.get("https://www.draegers.com/index.aspx")
    stores = driver.find_elements_by_css_selector('div.col-md-3.col-sm-6.center')
    for store in stores:
        location_name = store.find_element_by_css_selector('strong.subheader2').text
        raw_address = store.text
        tagged = usaddress.tag(raw_address)[0]
        try:
            street_address = tagged['BuildingName'].split('\n')[0] + " " + tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        except:
            try:
                street_address = tagged['BuildingName'].split('\n')[1]
            except:
                try:
                    street_address = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    street_address = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        try:
            city = tagged['PlaceName']
        except:
            city = tagged['BuildingName'].split('\n')[2]
        state = tagged['StateName']
        zipcode = tagged['ZipCode'].split('\n')[0]
        phone = tagged['SubaddressIdentifier'].split('\n')[0]
        geomap = store.find_element_by_css_selector('a').get_attribute('href')
        lat,lon = parse_geo(geomap)
        data.append([
             'https://www.draegers.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              lat,
              lon,
              '<MISSING>'
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()