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
    lon = re.findall(r'long=(--?[\d\.]*)', url)[0]
    lat = re.findall(r'lat=(-?[\d\.]*)', url)[0]
    return lat, lon



def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://www.gardenfreshmarket.com/store-locator.html")
    stores = driver.find_elements_by_css_selector('a.wsite-button.wsite-button-large.wsite-button-highlight')
    name = [stores[i].get_attribute('href') for i in range(1, len(stores))]
    for i in range(0, len(name)):
        driver.get(name[i])
        time.sleep(5)
        location_name = driver.find_element_by_css_selector('td:nth-child(1) > h2.wsite-content-title > font:nth-child(1)').text
        raw_address = driver.find_element_by_css_selector('td:nth-child(1) > h2.wsite-content-title > font:nth-child(3)').text
        try:
            raw_address = raw_address + " " + driver.find_element_by_css_selector('td:nth-child(1) > h2.wsite-content-title > font:nth-child(5)').text
        except:
            pass
        try:
            raw_address = raw_address + " " + driver.find_element_by_css_selector('td:nth-child(1) > h2.wsite-content-title > font:nth-child(7)').text
        except:
            pass
        tagged = usaddress.tag(raw_address)[0]
        try:
            street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0] + " " +tagged['StreetNamePostType'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0]
                except:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        state = tagged['StateName'].split()[0]
        city = tagged['PlaceName']
        try:
            phone = tagged['StateName'].split('\n')[1] + tagged['ZipCode']
        except:
            phone = tagged['StateName'].split(' ')[1] + tagged['ZipCode']
        geomap = driver.find_element_by_css_selector('div.wsite-map > iframe').get_attribute('src')
        lat, lon = parse_geo(geomap)
        hours_of_op = driver.find_element_by_css_selector('td:nth-child(2) > h2').text
        data.append([
             'http://www.gardenfreshmarket.com/',
              location_name,
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