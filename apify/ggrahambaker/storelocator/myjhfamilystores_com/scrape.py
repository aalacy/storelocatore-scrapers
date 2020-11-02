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
    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'http://www.myjhfamilystores.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.et_pb_row.et_pb_row_2')

    hrefs = main.find_elements_by_css_selector("a")

    link_list = []
    for h in hrefs:
        link_list.append(h.get_attribute('href'))

    all_store_data = []
    for link in link_list:

        driver.get(link)
        driver.implicitly_wait(10)

        try:
            cont = driver.find_element_by_css_selector(
            'div.et_pb_column.et_pb_column_3_4.et_pb_column_1.et_pb_css_mix_blend_mode_passthrough.et-last-child').text.split(
            '\n')
        except NoSuchElementException:
            continue
        location_name = cont[0]

        addy_phone = cont[1].split('|')

        addy = addy_phone[0]

        street_address, city, state, zip_code = parse_addy(addy)
        phone_number = addy_phone[1].replace('PHONE:', '').strip()

        href = driver.find_element_by_xpath("//a[contains(@href, 'maps.google')]").get_attribute('href')

        start = href.find('?ll=')
        if start > 0:
            end = href.find('&z=')
            coords = href[start + 4: end].split(',')
            lat = coords[0]
            longit = coords[1]

        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link
        hours = '<MISSING>'

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
