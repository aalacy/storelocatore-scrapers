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
    locator_domain = 'https://www.emcseafood.com/'
    ext = 'location/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.textwidget')
    all_store_data = []
    for div in divs:
        if 'ORDER ONLINE' in div.text:
            continue
        elif 'Please note that gift cards' in div.text:
            continue
        else:
            content = div.text.split('\n')
            if len(content) > 2:
                location_name = content[0].replace(' NOW OPEN', '').strip()
                parsed_add = usaddress.tag(content[1])[0]

                street_address = parsed_add['AddressNumber'] + ' ' + parsed_add['StreetName'] + ' '
                if 'StreetNamePostType' in parsed_add:
                    street_address += parsed_add['StreetNamePostType'] + ' '
                if 'OccupancyType' in parsed_add:
                    street_address += parsed_add['OccupancyType'] + ' '
                if 'OccupancyIdentifier' in parsed_add:
                    street_address += parsed_add['OccupancyIdentifier'] + ' '
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']

                phone_number = content[2].replace('tel:', '').strip()
                hours = ''
                for h in content[4:]:
                    hours += h + ' '

                href = div.find_element_by_css_selector('a').get_attribute('href')

                start_idx = href.find('/@')
                end_idx = href.find('z/data')
                if start_idx == -1:
                    start_idx = href.find('!ld')
                    if start_idx == -1:

                        lat = '<INACCESSIBLE>'
                        longit = '<INACCESSIBLE>'
                    else:
                        coords = href[start_idx + 3:].split('!2d')
                else:
                    coords = href[start_idx + 2: end_idx].split(',')
                    lat = coords[0]
                    longit = coords[1]

                country_code = 'US'
                store_number = '<MISSING>'
                location_type = '<MISSING>'

                if len(zip_code) == 6:
                    zip_code = zip_code[:-1]
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
