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
    driver.get("http://kentsgrocery.com/all")
    time.sleep(10)
    stores = driver.find_element_by_class_name("dropdown-menu").find_elements_by_tag_name('li')

    for i in stores:
        url=i.find_element_by_tag_name('a').get_attribute('href')
        driver.get(url)
        print(url)
        time.sleep(5)
        location_name = driver.find_element_by_id('theStoreName').text
        raw_address = driver.find_element_by_css_selector('#storeInfoContain > p:nth-child(2)').text
        tagged = usaddress.tag(raw_address)[0]
        try:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'].replace('\n', '')
            except:
                try:
                    street_addr = tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'].replace('\n', '')
                except:
                    try:
                        street_addr =  tagged['StreetName'].replace('\n', '')
                    except:
                        street_addr = "<MISSING>"
        state = tagged['StateName']
        city = tagged['PlaceName'].replace('\n', '')
        zipcode = tagged['ZipCode']
        phone = driver.find_element_by_css_selector('#storeInfoContain > p:nth-child(7) > a').text
        hours_of_op = driver.find_element_by_css_selector('#storeInfoContain > p:nth-child(4)').text + " " + driver.find_element_by_css_selector('#storeInfoContain > p:nth-child(5)').text
        geomap = driver.find_element_by_css_selector('#mapContain > iframe').get_attribute('src')
        lat,lon = parse_geo(geomap)
        data.append([
             'http://kentsgrocery.com/',
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
