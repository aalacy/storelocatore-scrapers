import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rascalhouse_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def parse_geo(url):
    lon = re.findall(r'\"lng":(-?[\d\.]*)', url)[0]
    lat = re.findall(r'\"lat":(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    #Variables
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('https://rascalhouse.com/')
    time.sleep(6)
    # Fetch stores 
    stores = driver.find_elements_by_class_name("title")
    location_name = [stores[i].get_attribute('innerText') for i in range(0,len(stores))]
    phones = driver.find_elements_by_class_name("phone")
    phone = [phones[i].get_attribute('innerText') for i in range(0,len(phones))]
    address = driver.find_elements_by_class_name("address")
    geomap =driver.find_elements_by_xpath("//script[@type='text/javascript']")
    geomaps = geomap[-2].get_attribute('innerHTML')
    latlon = re.findall(r'"point":{(.*?)\}', geomaps)
    for i in range(0,len(latlon)):
        lat,lon = parse_geo(latlon[i])
        latitude.append(lat)
        longitude.append(lon)
    
    for i in range(0,len(address)):
        #logger.info(location_name)
        a=address[i].get_attribute('innerText').split("\n")
        #logger.info(a)
        street_address.append(a[0])
        city.append(a[1].split(",")[0])
        state.append(a[1].split(",")[1].strip().split()[0])
        zipcode.append(a[1].split(",")[1].strip().split()[1])
        sep=","
        hours_of_operation.append(sep.join(a[2:]))
    for n in range(0,len(location_name)): 
        data.append([
            'https://rascalhouse.com/',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
