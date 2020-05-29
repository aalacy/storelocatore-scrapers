import csv
import os
from sgselenium import SgSelenium

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

def clean(arr):
    to_ret = []
    for a in arr:
        if 'Store Pickup' in a:
            continue
        elif 'View Weekly Ad' in a:
            continue

        to_ret.append(a)

    return to_ret

def fetch_data():
    locator_domain = 'https://www.amigosunited.com/'
    ext = 'Sysnify.Relationshop.v2/StoreLocation/SearchStore'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)

    source = str(driver.page_source)

    for line in source.splitlines():
        if line.strip().startswith("var stores"):
            stores = driver.execute_script(line + "; return stores")

    all_store_data = []
    for store in stores:
        street_address = store['Address1']
        city = store['City']
        lat = store['Latitude']
        longit = store['Longitude']
        phone_number = store['PhoneNumber']
        state = store['State']
        hours = store['StoreHours']
        location_type = store['StoreName']
        zip_code = store['Zipcode']

        country_code = 'US'
        store_number = '<MISSING>'
        location_name = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
