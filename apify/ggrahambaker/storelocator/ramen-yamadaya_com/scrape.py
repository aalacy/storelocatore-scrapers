import csv
import os
from sgselenium import SgSelenium
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.ramen-yamadaya.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    hrefs = driver.find_elements_by_xpath("//a[contains(text(),'VISIT STORE')]")
    hrefs.append(driver.find_element_by_xpath("//a[contains(text(),'visit store')]"))
    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        map_coord = driver.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map').get_attribute(
            'data-block-json')
        loc_json = json.loads(map_coord)

        lat = loc_json['location']['mapLat']
        longit = loc_json['location']['mapLng']
        street_address = loc_json['location']['addressLine1']
        city, state, zip_code = loc_json['location']['addressLine2'].split(',')
        state = state.strip()
        zip_code = zip_code.strip()

        location_name = loc_json['location']['addressTitle']

        divs = driver.find_elements_by_css_selector('div.sqs-block-content')
        for div in divs:
            if 'HOURS' in div.text:
                cont = div.text.split('\n')

                hours = ''
                for i, h in enumerate(cont):
                    if 'Phone' in h:
                        phone_number = cont[i + 1]
                        break
                    clean = ' '.join(h.split())
                    hours += clean + ' '

                hours = hours.replace('HOURS', '').strip()

        country_code = 'US'
        location_type = '<MISSING>'
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
