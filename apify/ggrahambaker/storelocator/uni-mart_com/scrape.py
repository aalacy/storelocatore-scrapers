import csv
import os
from sgselenium import SgSelenium

from selenium.common.exceptions import NoSuchElementException
import usaddress
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
    parsed_add = usaddress.tag(addy)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetNamePreType' in parsed_add:
        street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' '

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://uni-mart.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)
    not_found_result_top = True
    while not_found_result_top:
        try:
            loc_cont = driver.find_element_by_id('resulttop')
            not_found_result_top = False
        except NoSuchElementException:
            time.sleep(5)

    locs = loc_cont.find_elements_by_css_selector('span.mytool')
    link_list = []
    for l in locs:
        links = l.find_elements_by_css_selector('a')
        link = links[1].get_attribute('href')

        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        lat = '<MISSING>' #link[1][0]
        longit = '<MISSING>' #link[1][1]

        addy = driver.find_element_by_css_selector('div.address').find_element_by_css_selector(
            'span.locationaddress').text.replace('\n', ' ')

        addy = addy.replace('United States', '').strip()

        if '2693 Route 940 Pocono Summit' in addy:
            street_address = '2693 Route 940'
            city = 'Pocono Summit'
            state = 'Pennsylvania'
            zip_code = '18346'
        elif '1440 Easton Road RTE 611' in addy:
            street_address = '1440 Easton Road RTE 611'
            city = 'Riegelsville'
            state = 'Pennsylvania'
            zip_code = '18930'
        elif '16067 Ohio 170' in addy:
            street_address = '16067 Ohio 170'
            city = 'Calcutta'
            state = 'Ohio'
            zip_code = '43920'
        else:
            street_address, city, state, zip_code = parse_addy(addy)

        cut = link.find('uni-mart-')
        location_name = link[cut:].replace('-', ' ')

        country_code = 'US'

        phone_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        hours = '<MISSING>'
        store_number = link[cut + len('uni-mart-'):]

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
