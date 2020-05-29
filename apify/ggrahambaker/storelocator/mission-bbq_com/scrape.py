import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
import time
import usaddress


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
    locator_domain = 'https://mission-bbq.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)


    divs = driver.find_elements_by_css_selector('div.hidden-phone')
    hours = ''

    for div in divs:
        if 'Restaurant Hours:' in div.text:
            hours = div.text.replace('Restaurant Hours:', '').replace('\n', ' ').strip()


    drop_down = driver.find_element_by_id('categories-1')
    options = drop_down.find_elements_by_css_selector('option')

    states = []
    for opt in options:
        if 'Select State' in opt.text:
            continue

        states.append(opt.text)

    all_store_data = []
    for state in states:
        driver.get(locator_domain + ext)
        driver.implicitly_wait(10)
        drop_down = driver.find_element_by_id('categories-1')
        select = Select(drop_down)
        # select by visible text
        select.select_by_visible_text(state)
        driver.find_element_by_css_selector('button.button.button-primary.mission-search-button').click()
        driver.implicitly_wait(10)
        ## get store info

        drop_down = driver.find_element_by_id('limit')
        select = Select(drop_down)
        select.select_by_value('0')
        driver.implicitly_wait(10)

        locs = driver.find_elements_by_css_selector('div.grid-item.span4')

        for loc in locs:
            img_url = loc.find_element_by_css_selector('div.grid-content').find_element_by_css_selector(
                'img').get_attribute('src')

            if 'comingsoon' in img_url:
                continue

            cont = loc.find_element_by_css_selector('div.grid-item-name')
            location_name = cont.find_element_by_css_selector('h8').text

            divs = cont.find_elements_by_css_selector('div')
            addy = divs[0].text.replace('\n', ' ')

            street_address, city, state, zip_code = parse_addy(addy)

            href = divs[1].find_element_by_css_selector('a').get_attribute('href')

            start = href.find('/@')
            if start > 0:
                end = href.find('z/data')
                coords = href[start + 2:end].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

            if '.' not in longit:
                longit = '<MISSING>'
            if longit == '':
                longit = '<MISSING>'


            phone_number = divs[2].text.replace('Restaurant', '').strip()


            country_code = 'US'

            location_type = '<MISSING>'
            page_url = '<MISSING>'
            store_number = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours, page_url]
            all_store_data.append(store_data)

        time.sleep(2)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
