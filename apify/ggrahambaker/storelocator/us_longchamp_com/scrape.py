import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import usaddress
#

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
    if 'PlaceName' in parsed_add:
        city = parsed_add['PlaceName'].strip()
    else:
        city = '<MISSING>'

    state = '<MISSING>'
    zip_code = '<MISSING>'

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://us.longchamp.com/'
    ext = 'stores'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    stores = driver.find_elements_by_css_selector('li.bb-gray')
    link_list = []
    for store in stores:
        link = store.find_element_by_css_selector('a').get_attribute('href')
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        try:
            map_div = driver.find_element_by_css_selector('div#store-map')
        except NoSuchElementException:
            ## broken link
            continue
        lat = map_div.get_attribute('data-lat')
        longit = map_div.get_attribute('data-lon')
        if lat == '':
            lat = '<MISSING>'
        if longit == '':
            longit = '<MISSING>'

        hours_html = driver.find_element_by_css_selector('div.js-to_expand.animated-expandmore').get_attribute(
            'innerHTML')

        hours = BeautifulSoup(hours_html, 'html.parser').text

        if 'Facebook' in hours:
            hours = '<MISSING>'
        else:
            hours = hours.replace('\n', ' ').strip()

        location_name = driver.find_element_by_css_selector('h2.title-gamma.upper.pt-1.pb-05').text
        cont = driver.find_element_by_css_selector(
            'div.ff-light.mt-05.mb-1.js-accordion.accordion--beta.accordion').text.split('\n')

        phone_number = cont[-2].replace('(','').replace(')', '').replace('+1', '').replace('+', '')

        addy = cont[0]

        if '1870 REDWOOD HIGHWAY' in addy:
            street_address = '1870 REDWOOD HIGHWAY'
            city = 'CORTE MADERA'
        elif 'JFK AIRPORT TERMINAL' in addy:
            street_address = 'JFK AIRPORT TERMINAL 4'
            city = 'JAMAICA'
        elif '1 GARDEN STATE PLAZA' in addy:
            street_address = '1 GARDEN STATE PLAZA'
            city = 'PARAMUS'
        elif '550 STANFORD SHOPPING CENTER' in addy:
            street_address = '550 STANFORD SHOPPING CENTER '
            city = 'PALO ALTO'
        elif '3500 LAS VEGAS BD SOUTH ' in addy:
            street_address = '3500 LAS VEGAS BD SOUTH SUITE S33'
            city = 'LAS VEGAS'

        else:
            street_address, city, state, zip_code = parse_addy(addy)

        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
