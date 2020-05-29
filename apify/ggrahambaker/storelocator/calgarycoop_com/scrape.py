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
    locator_domain = 'https://www.calgarycoop.com'
    ext = '/stores/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    map_data = driver.execute_script('return mapData')

    all_store_data = []
    for loc in map_data:
        street_address = loc['address']

        if ',' in street_address:
            street_address = street_address.split(',')[1].strip()

        city_state = loc['city_prov'].split(',')
        city = city_state[0]
        state = city_state[1].strip()
        lat = loc['lat']
        longit = loc['lon']
        location_name = loc['name']
        zip_code = loc['postal']

        location_type = loc['services']

        country_code = 'CA'
        link = loc['link']
        driver.get(locator_domain + link)
        driver.implicitly_wait(10)

        main = driver.find_element_by_css_selector('div.store-department-wrapper')
        depts = main.find_elements_by_css_selector('div.store-department')
        hours = ''
        phone_switch = True
        for dept in depts:

            dept_type = dept.find_element_by_css_selector('h5').text
            hours += dept_type + ' '
            hour_info = dept.find_elements_by_css_selector('p')
            for hour in hour_info:
                if hour.get_attribute('class') == 'holiday-hours':
                    continue
                if 'Phone' in hour.text and phone_switch:
                    phone_number = hour.text.replace('\n', '').replace('Phone', '').strip()

                    phone_switch = False

                hours += hour.text.replace('\n', ' ') + ' '

        if 'Cardlock' in hours:
            hours = '<MISSING>'

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
