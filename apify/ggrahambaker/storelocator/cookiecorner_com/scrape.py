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
    locator_domain = 'https://cookiecorner.com/'
    ext = 'about/store_locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#main')
    content = main.text.split('\n')
    cycle = 0
    all_store_data = []
    for i, cont in enumerate(content[1:]):
        if cont == '':
            cycle = -1

            lat = '<MISSING>'
            longit = '<MISSING>'

            country_code = 'US'
            location_type = '<MISSING>'
            store_number = '<MISSING>'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

        elif cycle == 0:
            location_name = cont
        elif cycle == 1:
            phone_number = cont
        elif cycle == 2:
            if 'Kapolei' in cont:
                street_address = '91 - 590 Farrington Highway # 115'
                city = 'Kapolei'
                state = 'HI'
                zip_code = '96707'
            else:
                parsed_add = usaddress.tag(cont)[0]

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

                street_address = street_address.strip()
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                if 'ZipCode' in parsed_add:
                    zip_code = parsed_add['ZipCode']
                else:
                    zip_code = '<MISSING>'


        elif cycle == 4:
            hours = cont
        elif cycle == 5:
            hours += ' ' + cont

        cycle += 1


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
