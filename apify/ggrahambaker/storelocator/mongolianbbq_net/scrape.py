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

def fetch_data():
    locator_domain = 'http://mongolianbbq.net/'
    ext = 'locations.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'mapquest')]")
    all_store_data = []
    for h in hrefs:
        cont = h.text.split('\n')
        street_address = cont[0]
        city, state, zip_code = addy_ext(cont[1])
        phone_number = cont[2]

        hours = '11:30am - 9:00pm 7 days a week'

        lat = '<MISSING>'
        longit = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
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
