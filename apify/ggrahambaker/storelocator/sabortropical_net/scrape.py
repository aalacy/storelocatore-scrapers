import csv
import os
from sgselenium import SgSelenium
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
    parsed_add = usaddress.tag(addy)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetNamePreType' in parsed_add:
            street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' ' 

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code

def fetch_data():    
    locator_domain = 'http://sabortropical.net/'
    ext = 'tiendas.php'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    source = str(driver.page_source)
    for line in source.splitlines():
        if 'var location_string' in line.strip():
            loc_arr = driver.execute_script(line + "; return location_string").split(';')
            
    coord_dict = {}
    for loc in loc_arr:
        loc_info = loc.split(',')
        if len(loc_info) < 3:
            continue
        
        if 'No. ' in loc_info[0]:
            search = 'No. '
        else:
            search = 'No.'
        start = loc_info[0].find(search)
        index = loc_info[0][start + len(search): start + len(search) + 1]
        coord_dict[index] = [loc_info[1].strip(), loc_info[2].strip()]

    all_store_data = []
    main = driver.find_element_by_css_selector('div#comidas')
    locs = main.find_elements_by_css_selector('div.col-xl-4.col-sm-6.col-md-4.aligncenter')
    for loc in locs:
        cont = loc.text.split('\n')
         
        location_name = cont[0]
        if 'MANAGEMENT OFFICE' in location_name:
            continue
        else:
            location_type = 'STORE'
            store_number = location_name.split('#')[1]
            
        if len(cont) == 5:
            off = 0
            addy = cont[1]
        else:
            off = 1
            addy = cont[1] + ' ' + cont[2]

        street_address, city, state, zip_code = parse_addy(addy)
        hours = cont[off + 2] + ' ' + cont[off + 3]
        phone_number = cont[off + 4].replace('Phone:', '').strip()
    
        if store_number not in coord_dict:
            lat = '<MISSING>'
            longit = '<MISSING>'
        else:
            lat = coord_dict[store_number][0]
            longit = coord_dict[store_number][1]
        
        country_code = 'US'
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                            store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
