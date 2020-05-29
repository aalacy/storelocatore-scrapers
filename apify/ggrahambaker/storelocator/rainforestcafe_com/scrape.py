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
    state_zip = address[1].strip().split('  ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.rainforestcafe.com/'
    ext = 'locations.asp'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    element = driver.find_element_by_css_selector('a.fancybox-item.fancybox-close')
    driver.execute_script("arguments[0].click();", element)

    map_area = driver.find_element_by_css_selector('map')
    locs = map_area.find_elements_by_css_selector('area')
    link_list = []
    for loc in locs:
        link_list.append(loc.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        loc_result_area = driver.find_element_by_css_selector('div#right')
        locations = loc_result_area.find_elements_by_css_selector('p')
        for loc in locations:
            cont = loc.text.split('\n')

            if len(cont) > 1:
                location_name = cont[0]
                street_address = cont[1]
                city, state, zip_code = addy_ext(cont[2])
                phone_number = cont[3]

                country_code = 'US'
                store_number = '<MISSING>'
                hours = '<MISSING>'
                location_type = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
