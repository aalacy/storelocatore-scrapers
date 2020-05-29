import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException

import re
import usaddress

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def hours_extract(addy):
    # returns hours string
    hours_string = ''
    for i, ele in enumerate(addy):
        if 'Hours:' in ele:
            hours_string += ele + ' '
        elif 'am-' in ele:
            hours_string += ele + ' '
        elif 'pm-' in ele:
            hours_string += ele + ' '
        elif 'Closed' in ele:
            hours_string += ele + ' '
        elif ' – ' in ele:
            if 'Email' in ele:
                continue
            hours_string += ele + ' '
        elif 'Everyday' in ele:
            hours_string += ele + ' '
        elif ' to ' in ele:
            hours_string += ele + ' '

    return hours_string.replace('Hours:', '').replace('Regular', '').strip()

def fetch_data():
    locator_domain = 'http://www.jgumbos.com/'
    ext = 'location/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    loc_wrap = driver.find_element_by_css_selector('div.fusion-column-wrapper')

    alinks = loc_wrap.find_elements_by_css_selector('a')
    state_links = []
    for a in alinks:
        state_links.append(a.get_attribute('href'))

    store_links = []
    for state in state_links:
        driver.get(state)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div.post-content')
        stores = main.find_elements_by_css_selector('a')
        if len(stores) == 0:
            continue

        for store in stores:
            try:
                link = store.get_attribute('href')
                if '.png' in link:
                    continue
                if link in store_links:
                    continue
                store_links.append(link)
            except NoSuchElementException:
                print('no a tag')

    all_store_data = []
    for link in store_links:
        driver.get(link)
        driver.implicitly_wait(15)

        main = driver.find_element_by_css_selector('div.post-content')
        cont = main.find_element_by_css_selector('div.fusion-column-wrapper').text.split('\n')

        if len(cont) > 1:
            if 'Now Open' in cont[-1]:
                location_name = cont[0]
                street_address = cont[1]
                city, state, zip_code = addy_ext(cont[2])
                hours = '<MISSING>'
            else:
                location_name = cont[0]
                hours = hours_extract(cont)

                addy_cut = 0
                for i, add in enumerate(cont):
                    result1 = re.compile('\d{3}\-\d{3}')
                    result2 = re.compile('\(\d{3}\)\ \d{3}')
                    for m in result1.finditer(add):
                        phone_number = add[m.start():]
                        addy_cut = i
                    for m in result2.finditer(add):
                        phone_number = add[m.start():]
                        addy_cut = i

                clean_cont = cont[1:addy_cut]
                addy_string = ''
                zip_re = re.compile('\d{5}')
                to_break = False
                for i, addy in enumerate(clean_cont):
                    if to_break:
                        break

                    addy_string += addy + ' '
                    for m in zip_re.finditer(addy):
                        if m.group():
                            to_break = True

                parsed_add = usaddress.tag(addy_string)[0]

                street_address = ''

                if 'AddressNumber' in parsed_add:
                    street_address += parsed_add['AddressNumber'] + ' '
                if 'StreetNamePreDirectional' in parsed_add:
                    street_address += parsed_add['StreetNamePreDirectional'] + ' '
                if 'StreetName' in parsed_add:
                    street_address += parsed_add['StreetName'] + ' '
                if 'StreetNamePostType' in parsed_add:
                    street_address += parsed_add['StreetNamePostType'] + ' '
                if 'OccupancyType' in parsed_add:
                    street_address += parsed_add['OccupancyType'] + ' '
                if 'OccupancyIdentifier' in parsed_add:
                    street_address += parsed_add['OccupancyIdentifier'] + ' '
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']

            store_number = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            location_type = '<MISSING>'

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
