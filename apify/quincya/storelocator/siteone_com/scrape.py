from sgselenium import SgChrome
from bs4 import BeautifulSoup
import csv
import json

from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name='siteone.com')

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    driver = SgChrome().chrome()
    data = []

    locator_domain = 'siteone.com'

    for i in range(100):
        base_link = "https://www.siteone.com/store-finder?q=60101&miles=2000&page=%s" %i
        log.info(base_link)
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source,"lxml")
        
        try:
            stores = json.loads(base.text)['data']
        except:
            break

        for store in stores:
            location_name = store['name']
            street_address = (store['line1'] + " " + store['line2']).strip()
            city = store['town']
            state = store['regionCode']
            zip_code = store['postalCode']
            country_code = "US"
            store_number = store['storeId']
            location_type = "<MISSING>"
            phone = store['phone']

            hours = store['openings']
            hours_of_operation = ""
            for day in hours:
                hours_of_operation = (hours_of_operation + " " + day + " " + hours[day]).strip()
            if not hours_of_operation:
                hours_of_operation = '<MISSING>'

            latitude = store['latitude']
            longitude = store['longitude']

            link = "https://www.siteone.com/en/store/" + store_number

            data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
