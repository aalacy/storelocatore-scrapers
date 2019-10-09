import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

    street_address = street_address.strip()
    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


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

def fetch_data():
    locator_domain = 'http://www.pokeatery.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    link_list = []
    main = driver.find_element_by_css_selector('section.page__content.js-post-gallery.cf')
    hrefs = main.find_elements_by_css_selector('a')
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div.grid__item.eight-twelfths.palm-one-whole').text.split('\n')
        location_name = driver.find_element_by_css_selector('h1.headline__primary').text

        if len(main) == 12:
            hours = main[1]
            if 'Daily' not in hours:
                hours += ' ' + main[2]

            street_address = main[3]
            city, state, zip_code = addy_ext(main[4])

            phone_number = main[5]

        elif len(main) == 7:
            hours = main[0]

            end_address = main[1].find('(')
            end_phone = main[1].find('@')
            addy = main[1][:end_address]
            street_address, city, state, zip_code = parse_addy(addy)

            raw_phone = main[1][end_address:end_phone]
            phone_number = raw_phone[: raw_phone.find('-') + 5]

        else:
            hours = main[1] + ' ' + main[2]

            street_address = main[4]
            city, state, zip_code = addy_ext(main[5])
            phone_number = main[6]

        lat = '<MISSING>'
        longit = '<MISSING>'
        country_code = 'US'
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
