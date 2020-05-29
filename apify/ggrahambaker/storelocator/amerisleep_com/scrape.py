import csv
import os
from sgselenium import SgSelenium
import usaddress

def parse_address(addy_string):
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

    return street_address, city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.amerisleep.com/'
    ext = 'retail'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    states = driver.find_elements_by_css_selector('div.o-grid__item')
    link_href = []
    for state in states:
        links = state.find_elements_by_css_selector('a')
        for link in links:
            if 'jobs' in link.get_attribute('href'):
                continue
            elif '.html' in link.get_attribute('href'):
                continue
        
            else:
                link_href.append(link.get_attribute('href'))

    all_store_data = []
    for link in link_href:
        if 'careers' in link:
            continue
        driver.implicitly_wait(10)
        driver.get(link)

        location_name = driver.find_element_by_css_selector('.o-title--bemma').text

        addy = driver.find_element_by_css_selector('div.local-page__address').text.replace('\n', ' ')
        
        street_address, city, state, zip_code = parse_address(addy)
        
        hours = driver.find_element_by_css_selector('div.store-hours').text.replace('\n', ' ').strip()
        
        phone_numbers = driver.find_elements_by_xpath("//a[contains(@href, 'tel:')]")
        for num in phone_numbers:
            if '800' in num.text:
                temp_num = num.text
                continue
            phone_number = num.text
        
        if phone_number == '':
            phone_number = temp_num

        href = driver.find_element_by_css_selector('div#map-canvas').find_element_by_css_selector('iframe').get_attribute('src')
        start_idx = href.find('!2d')
        end_idx = href.find('!2m')
        if start_idx > -1:
            coords = href[start_idx + 3:end_idx].split('!3d')
            
            lat = coords[1]
            if '!3m' in lat:
                lat = lat.split('!3m')[0]
            longit = coords[0]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
