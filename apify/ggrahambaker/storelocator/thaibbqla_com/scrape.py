import csv
import os
from sgselenium import SgSelenium
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thaibbqla_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

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

    return street_address, city, state, zip_code

def clean_arr(arr):
    to_ret = []
    for a in arr:
        if 'DELIVERY' in a:
            continue
        if '(' in a:
            continue

        to_ret.append(a)

    return to_ret

def fetch_data():
    locator_domain = 'http://thaibbqla.com/'
    ext = 'location.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    strong = driver.find_element_by_xpath("//strong[contains(text(),'THAI ORIGINAL BBQ on 3RD STREET')]")
    ## up to p
    p = strong.find_element_by_xpath('..')
    ## up to td
    td = p.find_element_by_xpath('..')
    ## up to tr
    tr = td.find_element_by_xpath('..')
    ## up to body
    body = tr.find_element_by_xpath('..')

    # logger.info(body.text.split('\n'))
    p_cont = body.find_elements_by_css_selector('p')
    all_store_data = []
    hours = 'Sunday - Thursday 11:00 a.m. - 10:00 p.m. Friday & Saturday 11:00 a.m. - 11:00 p.m.'
    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'

    duplicate_tracker = []
    for i, c in enumerate(p_cont):

        cont = c.text.split('\n')

        if len(cont) == 13:
            location_name = cont[0]
            addy = cont[1] + ' ' + cont[2]
            street_address, city, state, zip_code = parse_address(addy)
            phone_number = cont[3].replace('T1:', '').strip()

            duplicate_tracker.append(location_name)
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

        elif len(cont) > 6:
            ## two locations
            spin = 0

            cont = clean_arr(cont)

            for c in cont:
                if 'THAI BBQ' in c:
                    spin = 0

                if spin == 0:
                    location_name = c
                elif spin == 1:
                    street_address, city, state, zip_code = parse_address(c)
                elif spin == 2:
                    cut_idx = c.find('FAX:')
                    phone_number = c[:cut_idx].replace('TEL:', '').strip()
                    duplicate_tracker.append(location_name)
                    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]

                    all_store_data.append(store_data)

                else:
                    ## do nothing
                    nothing = 0

                spin += 1

        else:
            if 'CATERING and PARTY TRAYS' in cont[0]:
                break
            if len(cont) < 2:
                continue

            location_name = cont[0]
            if location_name in duplicate_tracker:
                continue
            if '1109 PACIFIC COAST HIGHWAY' in cont[1]:
                addy = cont[1] + ' ' + cont[2]
                street_address, city, state, zip_code = parse_address(addy)
                cut_idx = cont[3].find('FAX:')
                phone_number = cont[3][:cut_idx].replace('TEL:', '').strip()
            elif '4116 DYER STR.' in cont[1]:
                addy = '4116 DYER STR. ' + cont[2]
                street_address, city, state, zip_code = parse_address(addy)
                cut_idx = cont[3].find('FAX:')
                phone_number = cont[3][:cut_idx].replace('TEL:', '').strip()
            else:
                street_address, city, state, zip_code = parse_address(cont[1])
                cut_idx = cont[2].find('FAX:')
                phone_number = cont[2][:cut_idx].replace('TEL:', '').strip()

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
