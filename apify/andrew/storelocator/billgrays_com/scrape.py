import csv
import os
import json
from selenium import webdriver

MISSING = "<MISSING>"
INACCESSIBLE = "<INACCESSIBLE>"
BILL_GRAYS_STORE_LOCATOR_URL = "https://www.billgrays.com/index.cfm?Page=Bill%20Grays%20Locations"

DRIVER = webdriver.Chrome(f'{os.path.dirname(os.path.abspath(__file__))}/chromedriver')

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_stores():
    DRIVER.get(BILL_GRAYS_STORE_LOCATOR_URL)
    script_el = DRIVER.find_element_by_xpath("//script[@type='application/ld+json']")
    script_dict = json.loads(script_el.get_attribute('innerHTML'))
    stores = script_dict['@graph']
    stores = stores[1:]
    names = [store['name'] for store in stores]
    import pdb; pdb.set_trace()
    pass

def fetch_data():
    data = []
    data.extend(fetch_stores())
    return data

def scrape():
    global DRIVER
    data = fetch_data()
    DRIVER.quit()
    write_output(data)

scrape()
