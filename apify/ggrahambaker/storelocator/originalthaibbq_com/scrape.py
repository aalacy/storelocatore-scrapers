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

def clean_arr(arr):
    to_ret = []
    for a in arr:
        if 'DELIVERY' in a:
            continue
        if 'WEB ADDRESS' in a:
            continue
        if 'HEART OF THAI TOWN' in a:
            continue

        to_ret.append(a)
    return to_ret

def fetch_data():
    locator_domain = 'http://originalthaibbq.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.entry-content')
    locs = main.find_elements_by_css_selector('p')
    all_store_data = []
    for loc in locs:
        cont = loc.text.split('\n')
        if len(cont) > 1:
            if 'THAI BBQ' in cont[0]:
                clean_cont = clean_arr(cont)
                location_name = clean_cont[0]
                if 'THAI BBQ OF UNION CITY' in location_name:
                    addy = clean_cont[1] + ' ' + clean_cont[2]
                    off = 1
                else:
                    addy = clean_cont[1]
                    off = 0

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

                phone_number = clean_cont[2 + off].replace('TEL:', '').strip()
                if 'FAX:' in phone_number:
                    phone_number = phone_number.split('FAX')[0]

                lat = '<MISSING>'
                longit = '<MISSING>'

                country_code = 'US'
                location_type = '<MISSING>'
                store_number = '<MISSING>'

                hours = 'Sunday – Thursday 11:00 a.m. – 10:00 p.m.* Friday & Saturday 11:00 a.m. – 11:00 p.m.* *May vary from location to location'
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
