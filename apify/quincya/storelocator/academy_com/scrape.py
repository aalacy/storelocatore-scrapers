import csv
import json
import time
from sgselenium import SgSelenium
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    driver = SgSelenium().chrome()
    time.sleep(2)

    base_link = "https://www.academy.com/api/stores?lat=31.96&lon=-99.90&rad=10000&bopisEnabledFlag=false"
    
    driver.get(base_link)
    time.sleep(4)

    base = BeautifulSoup(driver.page_source,"lxml")
    stores = json.loads(base.text.strip())["stores"]

    data = []
    locator_domain = "academy.com"

    for store in stores:
        location_name = store["properties"]['storeName']
        street_address = store["properties"]['streetAddress']
        city = store["properties"]['city']
        state = store["properties"]["stateCode"]
        zip_code = store["properties"]['zipCode']
        if len(zip_code) < 5:
            zip_code = "<MISSING>"
        country_code = store["properties"]['country']
        store_number = store["storeId"].split("-")[-1]
        location_type = "<MISSING>"
        phone = store["properties"]['phone']
        hours_of_operation = store["properties"]['storeHours']
        latitude = store['geometry']['coordinates'][0]
        longitude = store['geometry']['coordinates'][1]

        # Store data
        data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
