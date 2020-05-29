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
    locator_domain = 'https://deliastamales.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    alert_obj = driver.switch_to.alert

    alert_obj.accept()

    main = driver.find_element_by_css_selector('footer#footer')

    locs = main.find_elements_by_css_selector('div.location')
    all_store_data = []
    for loc in locs:
        content = loc.text.split('\n')
        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3]

        href = loc.find_element_by_css_selector('a').get_attribute('href')
        start_idx = href.find('/@')
        end_idx = href.find('z/d')
        coords = href[start_idx + 2: end_idx].split(',')
        lat = coords[0]
        longit = coords[1]

        hours = 'Monday - Saturday 6:00AM to 8:00PM Sunday 7:00 AM to 6:00PM'

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
