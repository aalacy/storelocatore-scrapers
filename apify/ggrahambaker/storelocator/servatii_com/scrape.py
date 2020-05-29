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

def usa_ext(parsed_add):
    street_address = parsed_add['AddressNumber'] + ' ' + parsed_add['StreetName'] + ' '
    street_address += parsed_add['StreetNamePostType']
    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']
    return street_address, city, state, zip_code


def fetch_data():
    locator_domain = 'http://servatii.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    foot = driver.find_element_by_css_selector('div.footer-widget')
    locs = foot.find_elements_by_css_selector('li')

    all_store_data = []
    for loc in locs:
        content = loc.text.split('\n')
        if len(content) > 1:
            if len(content) == 5:
                if 'White Oak' in content[0] or 'Crestview Hills' in content[0] or 'Fairfield' in content[0]:
                    ## ['Crestview Hills', '2941 Dixie Highway', 'Crestview Hills, Ky 41017',
                    location_name = content[0]
                    parsed_add = usaddress.tag(content[1] + ' ' + content[2])[0]
                    street_address, city, state, zip_code = usa_ext(parsed_add)
                    location_type = '<MISSING>'
                    hours = content[3]
                    phone_number = content[4]
                else:
                    location_name = content[0]
                    parsed_add = usaddress.tag(content[1])[0]
                    street_address, city, state, zip_code = usa_ext(parsed_add)
                    location_type = content[2]
                    hours = content[3]
                    phone_number = content[4]

            elif len(content) == 3:
                location_name = content[0]
                cut_idx = content[1].find('WEDDING')
                to_tag = content[1][:cut_idx]

                parsed_add = usaddress.tag(to_tag)[0]
                street_address, city, state, zip_code = usa_ext(parsed_add)
                cut_idx2 = content[1].find('STORE')

                location_type = content[1][cut_idx:cut_idx2 + 6]

                hours = content[1][cut_idx2 + 6:]
                phone_number = content[2]
            elif len(content) == 8:
                location_name = content[0]
                parsed_add = usaddress.tag(content[1] + ' ' + content[2])[0]
                street_address, city, state, zip_code = usa_ext(parsed_add)
                location_type = content[3]
                hours = content[4] + ' ' + content[5] + ' ' + content[6]
                phone_number = content[7]
            elif len(content) == 6:
                location_name = content[0]
                parsed_add = usaddress.tag(content[1] + ' ' + content[2])[0]
                street_address, city, state, zip_code = usa_ext(parsed_add)
                location_type = content[3]
                hours = content[4]
                phone_number = content[5]

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
