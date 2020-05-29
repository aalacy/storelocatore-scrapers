import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
import usaddress

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
    locator_domain = 'https://meadowsfarms.com/'
    ext = 'garden-centers/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, '/garden-centers/locations?')]")
    region_list = []
    for h in hrefs:
        region_list.append(h.get_attribute('href'))

    link_list = []
    for region in region_list:
        driver.get(region)
        driver.implicitly_wait(10)
        hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'meadowsfarms.com/locations/')]")
        for h in hrefs:
            link = h.get_attribute('href')
            if link not in link_list:
                link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(30)

        location_name = driver.find_element_by_css_selector('div.masthead-caption').text

        try:
            href = driver.find_element_by_xpath("//a[contains(@href, 'maps.google.com/')]").get_attribute('href')
            start = href.find('ll=')
            end = href.find('&z=')
            coords = href[start + 3:end].split(',')
            lat = coords[0]
            longit = coords[1]
        except NoSuchElementException:
            lat = '<MISSING>'
            longit = '<MISSING>'

        addy = driver.find_element_by_css_selector('div.locationDetailBody-address').text.replace('\n', ' ')

        street_address, city, state, zip_code = parse_addy(addy)

        phone_number = driver.find_element_by_css_selector('a.phone').text

        try:
            hours = driver.find_element_by_css_selector('div.locationDetailBody-hours').text.replace(
                'Hours of Operation', '').replace('\n', ' ').strip()
        except NoSuchElementException:
            hours = '<MISSING>'

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link

        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
