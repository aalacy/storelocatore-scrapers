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


def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://www.meltshop.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()

    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    pop_up = driver.find_element_by_css_selector('a.sqs-popup-overlay-close')
    driver.execute_script("arguments[0].click();", pop_up)

    locs = driver.find_elements_by_css_selector('div.summary-item')
    all_store_data = []
    for i, loc in enumerate(locs):
        ps = loc.find_element_by_css_selector('div.summary-excerpt').find_elements_by_css_selector('p')
        location_name = loc.find_element_by_css_selector('div.summary-title').text
        hours = ps[0].text.replace('\n', ' ')
        address = ps[1].text.split('\n')

        if len(address) < 4:
            if 'Union' in address[0]:
                street_address = address[1]
                city, state, zip_code = addy_extractor(address[2])
                phone_number = '<MISSING>'
            elif 'Smith' in address[0]:
                continue
            elif 'Eagle' in address[0]:
                street_address = address[0]
                city, state, zip_code = addy_extractor(address[1])
                phone_number = address[2]
        else:
            if i < 4:
                street_address = address[0].split(',')[0]
            else:
                street_address = address[1].split(',')[0]
            city, state, zip_code = addy_extractor(address[2])
            phone_number = address[3]

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
