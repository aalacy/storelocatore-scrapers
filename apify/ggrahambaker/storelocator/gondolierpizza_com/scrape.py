import csv
import os
from sgselenium import SgSelenium

from bs4 import BeautifulSoup
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def add_to_arr(street_address, city, state, zip_code, phone_number):
    locator_domain = 'https://gondolierpizza.com/'
    location_name = '<MISSING>'
    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'
    hours = '<MISSING>'
    page_url = '<MISSING>'

    return [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours, page_url]

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
    zip_code = parsed_add['ZipCode'].replace('\\n', '').strip()
    
    return street_address, city, state, zip_code
    
def fetch_data():
    locator_domain = 'https://gondolierpizza.com/'
    ext = 'gondolier-pizza-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    source = str(driver.page_source.encode("utf-8"))
    soup = BeautifulSoup(source, 'html.parser')

    main = soup.find('div', {'class': 'post_content'})
    cont = main.find_all('p')
    all_store_data = []
    dup_tracker = []
    for i, c in enumerate(cont):
        if 'Gondolier Italian' in c.text:
            continue
        if 'Address:' in c.text:
           
            street_address, city, state, zip_code = parse_addy(c.text.replace('Address:', '').strip())
        if 'Phone:' in c.text:
            phone_number = c.text.replace('Phone:', '').strip()
            ## add to arr
            if street_address not in dup_tracker:
                dup_tracker.append(street_address)
                store_data = add_to_arr(street_address, city, state, zip_code, phone_number)
                all_store_data.append(store_data)
            else:
                continue
            
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
