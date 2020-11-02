import csv
import re
from sgselenium import SgSelenium
import json
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('highlandparkmarket_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.highlandparkmarket.com/'
    ext = 'contact'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)
    if '860-674-9536' in str(driver.page_source):
        logger.info('here')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    stores = soup.find_all('div', {'class': 'row sqs-row'})
    #stores = driver.find_elements_by_class_name('row sqs-row')
    logger.info(len(stores))
    del stores[8]
    del stores[7]
    del stores[6]
    del stores[2]
    del stores[0]
    all_store_data = []
    coords = soup.find_all('div', {'class': 'sqs-block map-block sqs-block-map'})
    for store in stores:
        content = re.sub(r'([a-z])([A-Z])',r'\1 \2',store.text.strip())
        content = re.sub(r'([a-z])(\d)', r'\1 \2',content)
        logger.info(len(content))
        logger.info(content)
        jc=coords[stores.index(store)].get('data-block-json')
        j_coords = json.loads(jc)
        location_name = re.findall(r'([a-zA-Z]+) \d',content.split(',')[0])[0]
        content=content.replace(str(location_name),'')
        lat = j_coords['location']['markerLat']
        longit = j_coords['location']['markerLng']
        logger.info(lat,longit)
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        city=location_name
        street_address, state, zip_code,hours,phone_number=re.findall(r'(.*), ([A-Z]{2}) ([\d]{5}).*Store Hours:(.*) Telephone: ([\-\d]+)',content)[0]
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)


    driver.quit()
    logger.info(all_store_data)
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
