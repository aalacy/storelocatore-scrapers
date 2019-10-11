import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
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
    if 'Old Bridge' in addy:
        street_address = '3500 Route 9'
        city = 'Old Bridge'
        state = 'NJ'
        zip_code = '08857'

    else:
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

    return street_address.strip(), city, state, zip_code


def format_hours(hours_arr):
    hours = ''
    for element in hours_arr:
        if 'Day of the Week' in element:
            continue
        if 'Today' in element:
            continue

        space_split = element.split(' ')
        if 'Open 24 hours' in element:
            hours += element + ' '
        elif len(space_split) == 3:
            # this means day
            hours += space_split[0] + ' '
        else:
            hours += element + ' '

    return hours.strip()



def fetch_data():
    locator_domain = 'https://local.acmemarkets.com/'
    ext = 'index.html'

    driver = get_driver()
    driver.get(locator_domain + ext)

    states = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
    state_list = []
    for state in states:
        state_list.append(state.get_attribute('href'))

    city_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        cities = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')

        for city in cities:
            city_list.append(city.get_attribute('href'))

    all_store_data = []
    for i, city in enumerate(city_list):
        driver.get(city)
        driver.implicitly_wait(10)

        try:
            lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
            longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        except NoSuchElementException:
            more_links = driver.find_elements_by_css_selector('a.Teaser-nameLink')
            for link in more_links:
                city_list.append(link.get_attribute('href'))
            continue


        addy = driver.find_element_by_css_selector('address').text.replace('\n', ' ')

        street_address, city, state, zip_code = parse_addy(addy)

        phone_number = driver.find_element_by_css_selector('span#telephone').text


        hours_table = driver.find_element_by_css_selector('table.c-location-hours-details').text.split('\n')

        hours = format_hours(hours_table)

        pharm = driver.find_elements_by_css_selector('a.LocationInfo-pharmacyLink')
        if len(pharm) == 0:
            location_type = 'Store'
        else:
            location_type = 'Store and Pharmacy'

        store_number = '<MISSING>'
        country_code = 'US'

        location_name = driver.find_element_by_css_selector('span.LocationName-geo').text

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
