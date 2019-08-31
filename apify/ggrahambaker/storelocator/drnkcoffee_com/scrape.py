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

def fetch_data():
    locator_domain = 'https://drnkcoffee.com/'
    ext = 'store-locations'

    driver = get_driver()
    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('div.grid90p.aligncenter.storedist')

    rows = main.find_elements_by_css_selector('div.row.clearfix.location_row')

    all_store_data = []
    for i, row in enumerate(rows[:-3]):
        content = row.text.split('\n')

        if len(content) == 12:
            to_spin = [content[:4], content[4:8], content[8:]]
            for store in to_spin:
                location_name = store[0]
                phone_number = store[2].replace('Phone:', '').strip()

                parsed_add = usaddress.tag(store[3])[0]

                street_address = ''
                street_address += parsed_add['AddressNumber'] + ' '
                if 'StreetNamePreDirectional' in parsed_add:
                    street_address += parsed_add['StreetNamePreDirectional'] + ' '
                if 'LandmarkName' in parsed_add:
                    street_address += parsed_add['LandmarkName'] + ' '
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
                lat = '<MISSING>'
                longit = '<MISSING>'

                country_code = 'US'
                location_type = '<MISSING>'
                store_number = '<MISSING>'
                hours = '<MISSING>'
                if 'Little Elm' in location_name:
                    zip_code = '75068'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

        else:
            to_spin = [content[:4], content[4:9], content[-4:]]
            for store in to_spin:
                location_name = store[0]
                phone_number = store[-2].replace('Phone:', '').strip()

                parsed_add = usaddress.tag(store[-1])[0]

                street_address = ''
                if 'AddressNumber' in parsed_add:
                    street_address += parsed_add['AddressNumber'] + ' '
                if 'StreetNamePreDirectional' in parsed_add:
                    street_address += parsed_add['StreetNamePreDirectional'] + ' '
                if 'LandmarkName' in parsed_add:
                    street_address += parsed_add['LandmarkName'] + ' '
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
                lat = '<MISSING>'
                longit = '<MISSING>'

                country_code = 'US'
                location_type = '<MISSING>'
                store_number = '<MISSING>'
                hours = '<MISSING>'
                if 'Little Elm' in location_name:
                    zip_code = '75068'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
