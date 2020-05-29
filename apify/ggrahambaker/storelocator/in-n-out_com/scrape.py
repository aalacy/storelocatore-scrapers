import csv
import os
from sgselenium import SgSelenium
from sgrequests import SgRequests
import json
import time

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url", "operating_info"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://in-n-out.com/'

    driver = SgSelenium().chrome()
    driver.get('https://locations.in-n-out.com/map/')
    driver.implicitly_wait(30)
    all_store = driver.find_element_by_css_selector('li#tabAll')
    driver.execute_script("arguments[0].click();", all_store)
    time.sleep(10)

    results = driver.find_elements_by_css_selector('div.result')
    store_numbers = []
    for res in results:
        store_number = res.get_attribute('data-storenumber')
        
        store_numbers.append(store_number)

    api_base = 'https://locations.in-n-out.com/api/finder/get/'
    all_store_data = []
    for store_number in store_numbers:
        response = session.get(api_base + store_number).content
        cont = json.loads(response)
        
        store_number = cont['StoreNumber']
        location_name = cont['Name']
        street_address = cont['StreetAddress']

        city = cont['City']
        state = cont['State']
        zip_code = cont['ZipCode']
        lat = cont['Latitude']
        longit = cont['Longitude']
        hours = ''
        for day in cont['DiningRoomNormalHours']:
            hours += day['Name'] + ': ' + day['Hours'] + ' '

        location_type = '<MISSING>'
        phone_number = '1-800-786-1000'
        page_url = '<MISSING>'
        country_code = 'US'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url, cont['DiningRoomHours']]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
