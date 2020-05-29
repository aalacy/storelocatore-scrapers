import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://famoso.ca/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    prov_selects = driver.find_element_by_css_selector('ul.provSelect')
    provs = prov_selects.find_elements_by_css_selector('li')
    prov_list = []
    for prov in provs:
        link = prov.find_element_by_css_selector('a').get_attribute('href')
        prov_list.append(link)

    link_list = []
    for prov in prov_list:
        driver.get(prov)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('ul.locations')
        links = main.find_elements_by_css_selector('a.highlighted')
        for link in links:
            link_list.append(link.get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(30)

        try:
            coords = driver.find_element_by_id('map_marker')
            lat = coords.get_attribute('data-lat')
            longit = coords.get_attribute('data-lng')
        except NoSuchElementException:
            lat = '<MISSING>'
            longit = '<MISSING>'

        phone_number = driver.find_element_by_css_selector('div.location-contacts.phone').find_element_by_css_selector(
            'a').text

        address = driver.find_element_by_css_selector('div.location-contacts.location').text.replace('Get directions\n',
                                                                                                     '').replace(
            'LOCATION\n', '')

        addy = address.split('\n')
        street_address = addy[0]
        zip_code = ''
        if 'West Edmonton Mall' in street_address:
            street_address = addy[1]
            city_prov = addy[2].split(' ')
            city = city_prov[0]
            state = city_prov[1]
        elif 'Suite 125,' in street_address:
            street_address += ' ' + addy[1]
            city_prov = addy[2].split(' ')
            city = city_prov[0]
            state = city_prov[1]
        elif 'Airport' in street_address:
            street_address += ' ' + addy[1]
            city_prov = addy[2].split(' ')

            city = city_prov[0] + ' ' + city_prov[1]
            state = city_prov[2]

        elif 'Unit 105 - 3030' in street_address:
            city = addy[1]
            zip_state = addy[2].split(' ')
            zip_code = zip_state[0] + ' ' + zip_state[1]
            state = zip_state[2]

        else:
            city_prov = addy[1].split(' ')
            if len(city_prov) == 2:
                city = city_prov[0]
                state = city_prov[1]
            elif len(city_prov) == 3:
                city = city_prov[0] + ' ' + city_prov[1]
                state = city_prov[2]

            else:
                city = addy[1]
                state = addy[2]

        if zip_code == '':
            zip_code = '<MISSING>'

        hours = driver.find_element_by_css_selector('ul.hours-list').text.replace('\n', ' ')

        start_idx = link.find('s/')
        location_name = link[start_idx + 2:-1].replace('-', ' ')

        country_code = 'CA'
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
