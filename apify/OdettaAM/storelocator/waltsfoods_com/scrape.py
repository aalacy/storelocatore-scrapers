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
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.waltsfoods.com/locations")
    hours_of_operation = driver.find_element_by_css_selector('div.et_pb_module.et_pb_text.et_pb_text_2.et_pb_bg_layout_light.et_pb_text_align_left > div.et_pb_text_inner > p').get_attribute('innerHTML')
    hours_of_operation = hours_of_operation.split('<br>\n')[0]+hours_of_operation.split('<br>\n')[1]
    stores = driver.find_elements_by_id('red')
    for store in stores:
        location_name = store.find_element_by_css_selector('div.et_pb_text_inner > h4').text
        if location_name != (""):
            tagged = usaddress.tag(store.find_element_by_css_selector('div.et_pb_text_inner > p').text)[0]
            try:
                street_address = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
            except:
                try:
                    street_address = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    street_address = tagged['AddressNumber'] + " " + tagged['StreetNamePostType'].split('\n')[0]
            city = tagged['PlaceName']
            state = tagged['StateName']
            zipcode = tagged['ZipCode'].split('\n')[0]
            phone = tagged['OccupancyIdentifier']
            data.append([
             'https://www.waltsfoods.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              '<INACCESSIBLE>',
              '<INACCESSIBLE>',
              hours_of_operation
            ])
    # Retrieve latitude and longitude for all locations
    geomaps = driver.find_elements_by_css_selector('div.et_pb_text_inner > p > iframe')
    i = 0
    while i < len(data):
        lat, lon = parse_geo(geomaps[i].get_attribute('src'))
        data[i][10] = lat
        data[i][11] = lon
        i += 1

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()