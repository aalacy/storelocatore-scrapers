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
    locator_domain = 'https://www.kreationjuice.com/'
    ext = 'pages/locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    heading_list = driver.find_elements_by_xpath('//h3[@data-pf-type="Heading"]')

    stores_lists = driver.find_elements_by_xpath('//ul[@data-pf-type="List"]')

    all_store_data = []
    for i, store_list in enumerate(stores_lists):
        location_type = heading_list[i].text
        stores = store_list.find_elements_by_css_selector('span')
        for store in stores:
            cont = store.text.split('\n')
            if len(cont) == 1:
                continue

            else:
                location_name = cont[0]
                addy = cont[1]

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
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']

                if len(zip_code) < 5:
                    zip_code = '<MISSING>'

                phone_number = cont[2]
                hours = cont[3]

                store_number = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'

                country_code = 'US'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]

                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
