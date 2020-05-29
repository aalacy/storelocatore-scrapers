import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def usc_parse(driver, link, locator_domain):
    driver.get(link)
    driver.implicitly_wait(10)

    body = driver.find_element_by_css_selector('body').text.split('\n')[5:]

    location_name = body[0]
    addy = body[1].split('.')

    street_address = addy[0] + addy[1]
    city, state, zip_code = addy_ext(addy[2])
    phone_number = body[3].replace('Phone Number:', '').strip()
    hours = body[7] + ' ' + body[8]

    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    longit = '<MISSING>'
    lat = '<MISSING>'

    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]

    return store_data

def sunset_parse(driver, link, locator_domain):
    driver.get(link)
    driver.implicitly_wait(10)

    sections = driver.find_elements_by_css_selector('section')
    for section in sections:
        if 'Address' in section.text:
            info = section.text.split('\n')
            street_address = info[1]
            city, state, zip_code = addy_ext(info[2])
            phone_number = info[3]
            hours = info[5] + ' ' + info[6]

            location_name = 'Sunset'
            country_code = 'US'
            location_type = '<MISSING>'
            store_number = '<MISSING>'
            longit = '<MISSING>'
            lat = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]

            return store_data

def vegas_parse(driver, link, locator_domain):
    # las vegas
    driver.get(link)
    driver.implicitly_wait(10)

    info = driver.find_element_by_css_selector('div.intro-txt-addy').text.split('\n')

    addy = info[0].split(',')
    street_address = addy[0]
    city = addy[1].strip()
    state_zip = addy[2].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]

    hours = info[1]

    phone_number = driver.find_element_by_css_selector('div.footer-item').text.split('\n')[-1]

    location_name = 'Las Vegas'
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    longit = '<MISSING>'
    lat = '<MISSING>'

    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]

    return store_data

def fetch_data():
    locator_domain = 'rockandreillys.com/'
    las_vegas = 'http://www.rockandreillyslv.com/'
    sunset = 'https://rockandreillys.com/'
    usc = 'https://rockandreillys.com/usc/'
    driver = SgSelenium().chrome()

    vegas_list = vegas_parse(driver, las_vegas, locator_domain)
    sunset_list = sunset_parse(driver, sunset, locator_domain)
    usc_list = usc_parse(driver, usc, locator_domain)

    all_store_data = [vegas_list, sunset_list, usc_list]

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
