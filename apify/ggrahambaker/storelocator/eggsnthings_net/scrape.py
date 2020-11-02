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
    zip_code = state_zip[1][:-1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://eggsnthings.net/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    main_divs = driver.find_elements_by_css_selector('section.vc_section')
    for div in main_divs:
        content = div.text.split('\n')
        if len(content) > 1:
            if len(content) == 16:
                cont_arr = [content[0:8], content[8:]]
            else:
                cont_arr = [content]

            for cont in cont_arr:
                location_name = cont[0]
                street_address = cont[1].replace('Address-', '').strip()
                city, state, zip_code = addy_ext(cont[2])
                phone_number = cont[3].replace('Phone:', '').strip()

                hours = cont[5] + ' ' + cont[6] + ' ' + cont[7]

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
