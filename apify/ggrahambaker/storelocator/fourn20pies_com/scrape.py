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

def fetch_data():
    locator_domain = 'http://www.fourn20pies.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    body = driver.find_element_by_css_selector('table#Table1')
    tds = body.find_elements_by_css_selector('td')

    all_store_data = []
    for td in tds:
        content = td.text.split('\n')
        if len(content) > 1:
            street_address = content[0]
            address = content[1].split(',')
            city = address[0]
            state = address[1].strip()
            zip_code = '<MISSING>'
            phone_number = content[3]
            hours = ''
            for h in content[5:]:
                hours += h + ' '
            hours = hours.strip()
            lat = '<MISSING>'
            longit = '<MISSING>'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            location_name = '<MISSING>'
            country_code = 'US'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
