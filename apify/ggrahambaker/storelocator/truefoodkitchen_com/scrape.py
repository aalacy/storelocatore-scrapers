import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    locator_domain = 'https://www.truefoodkitchen.com/'
    ext = 'locations'

    driver = get_driver()
    driver.get(locator_domain + ext)

    loc_section = driver.find_element_by_css_selector('section.accordion')
    links = loc_section.find_elements_by_css_selector('a')
    link_list = []
    for link in links:

        href = link.get_attribute('href')
        if 'goo' in href:
            continue
        if 'tel:' in href:
            continue

        loc_name = link.get_attribute('aria-label').replace('- Location Page', '').strip()
        link_list.append([href, loc_name])

    all_store_data = []
    for link in link_list:
        driver.get(link[0])
        driver.implicitly_wait(10)

        google_link = driver.find_element_by_css_selector('div.fullmap2').find_element_by_css_selector(
            'iframe').get_attribute('src')

        start_idx = google_link.find('!2d')
        end_idx = google_link.find('!2m')
        if end_idx < 0:
            end_idx = google_link.find('!3m')

        coords = google_link[start_idx + 3: end_idx].split('!3d')
        lat = coords[1]
        longit = coords[0]

        addy_info = driver.find_element_by_css_selector('div.address-info').find_elements_by_css_selector('li')

        phone_number = addy_info[0].text
        addy = addy_info[1].text.replace('\n', ' ')

        if addy == '':
            continue

        addy = addy.replace('| Tampa, FL 33607', '')
        if '120 Broadway Lane, Building 4, Space 1044' in addy:
            street_address = '120 Broadway Lane, Building 4, Space 1044'
            city = 'Walnut Creek'
            state = 'CA'
            zip_code = '94596'
        else:
            street_address, city, state, zip_code = parse_addy(addy)

        hours = addy_info[2].text.replace('\n', ' ')


        if hours == '':
            hours = '<MISSING>'


        loc_info = driver.find_element_by_id('location').find_element_by_css_selector('h2').text
        
        if 'COMING' in loc_info or 'OPENING' in loc_info:
            hours = loc_info

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        location_name = link[1]

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
