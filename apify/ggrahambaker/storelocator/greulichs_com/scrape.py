import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.greulichs.com/'
    ext = 'Contact/Find-Us'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []

    locs = driver.find_elements_by_css_selector('div.loclisting')
    for loc in locs:
        
        coord_element = loc.find_element_by_css_selector('span.distance')
        longit = coord_element.get_attribute('lon')
        lat = coord_element.get_attribute('lat')

        content = loc.text.split('\n')
        location_name = content[1]
        street_address = content[3]

        city, state, zip_code = addy_extractor(content[4])
        hours = ''
        for h in content[6:13]:
            hours += h + ' '

        phone_number = content[-4]

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
