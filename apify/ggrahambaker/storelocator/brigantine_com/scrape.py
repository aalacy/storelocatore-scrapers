import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://www.brigantine.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    locs = driver.find_elements_by_css_selector('div.location')
    all_store_data = []
    for loc in locs:
        cont = loc.text.split('\n')
        location_name = cont[0].split('(')[0].strip()
        phone_number = cont[1]
        street_address = cont[2]
        city = cont[3]
        state = cont[4]
        zip_code = cont[5]
        hours_div = loc.find_element_by_xpath('//div[@class="list-location"]')
        hours_html = driver.execute_script("return arguments[0].innerHTML", hours_div)
        soup = BeautifulSoup(hours_html, 'html.parser')

        hours = soup.text.replace('\n', ' ').strip()

        lat = '<MISSING>'
        longit = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
