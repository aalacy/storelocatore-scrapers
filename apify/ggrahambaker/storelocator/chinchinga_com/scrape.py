import csv
import os
from sgselenium import SgSelenium
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.chinchinga.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    bottom = driver.find_element_by_css_selector('section.bottom').find_element_by_css_selector('div')
    divs = bottom.find_elements_by_css_selector('div')

    all_store_data = []
    rucker = divs[:6]
    brook = divs[6:]
    for i, r in enumerate(rucker):
        content = r.text.split('\n')
        if i == 0:
            location_name = content[0]
            addy = content[1].replace('Chin Chin Chinese Restaurant - ', '')
            parsed_add = usaddress.tag(addy)[0]

            street_address = ''
            street_address += parsed_add['AddressNumber'] + ' '
            if 'StreetNamePreDirectional' in parsed_add:
                street_address += parsed_add['StreetNamePreDirectional'] + ' '

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

        elif i == 1:
            hours = ''
            for h in content[1:]:
                hours += h + ' '

            hours = hours.strip()

        elif i == 4:
            phone_number = content[1]
            lat = '<MISSING>'
            longit = '<MISSING>'

            country_code = 'US'
            location_type = '<MISSING>'
            store_number = '<MISSING>'
            zip_code = '30004'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)
        else:
            continue

    for i, b in enumerate(brook):
        content = b.text.split('\n')

        if i == 0:
            location_name = content[0]
            addy = content[1].replace('Chin Chin Chinese Restaurant - ', '')
            parsed_add = usaddress.tag(addy)[0]

            street_address = ''
            street_address += parsed_add['AddressNumber'] + ' '
            if 'StreetNamePreDirectional' in parsed_add:
                street_address += parsed_add['StreetNamePreDirectional'] + ' '

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

        elif i == 1:
            hours = ''
            for h in content[1:]:
                hours += h + ' '

            hours = hours.strip()

        elif i == 4:
            phone_number = content[1]
            lat = '<MISSING>'
            longit = '<MISSING>'

            country_code = 'US'
            location_type = '<MISSING>'
            store_number = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)
        else:
            continue

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
