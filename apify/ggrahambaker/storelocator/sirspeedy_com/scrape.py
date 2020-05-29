import csv
import os
from sgselenium import SgSelenium
import usaddress
from selenium.common.exceptions import NoSuchElementException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.sirspeedy.com/'
    ext = 'find-locator/#all_locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#locations_columns')
    locs = main.find_elements_by_css_selector('li')
    link_list = []
    for loc in locs:
        link = loc.find_element_by_css_selector('a').get_attribute('href')
        link_list.append(link)

    all_store_data = []
    duplicate_checker = []

    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        print(i, link)
        try:
            addy = driver.find_element_by_css_selector('p.location_address').text.replace('\n', ' ').replace('-', ' ')

            if '375 Worcester Rd.' in addy:
                street_address = '375 Worcester Rd. Route 9 West'
                city = 'Framingham'
                state = 'MA'
                zip_code = '01701'

            else:
                if '600 Huron Ave.' in addy:
                    addy = addy.replace('at Bard', '').strip()
                if '5505 North Crescent Blvd' in addy:
                    addy = addy.replace('Located on Route 130', '').strip()

                parsed_add = usaddress.tag(addy)[0]

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

                street_address = street_address.strip()
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']

            hours = driver.find_element_by_css_selector('p.store_hours').text.replace('\n', ' ').replace('Store Hours:',
                                                                                                         '').strip()
            phone_number = driver.find_element_by_css_selector('li.location-icon-phone').text

            longit = driver.find_element_by_css_selector('input.hiddenCenterLong').get_attribute('value')
            lat = driver.find_element_by_css_selector('input.hiddenCenterLat').get_attribute('value')
            location_type = 'Sir Speedy'
        except NoSuchElementException:
            try:
                addy = driver.find_element_by_css_selector('ul.location_address').text.replace('\n', ' ')

                parsed_add = usaddress.tag(addy)[0]

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

                street_address = street_address.strip()

                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']

                hours = driver.find_element_by_css_selector('ul.location_hours').text.replace('\n', ' ').replace('Store Hours:',
                                                                                                             '').strip()
                phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text.replace('P:', '').strip()

                longit = driver.find_element_by_css_selector('input.hiddenCenterLong').get_attribute('value')
                lat = driver.find_element_by_css_selector('input.hiddenCenterLat').get_attribute('value')
                location_type = 'Pip'
            except NoSuchElementException:
                ## no location
                continue

        location_name = '<MISSING>'
        store_number = '<MISSING>'

        country_code = 'US'

        if street_address not in duplicate_checker:
            duplicate_checker.append(street_address)
        else:
            continue
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
