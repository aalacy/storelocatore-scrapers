import csv
import os
from sgselenium import SgSelenium
import usaddress

def addy_parser(addy):
    parsed_add = usaddress.tag(addy)[0]

    if '600 W Chicago, Chicago 60654' in addy:
        street_address = '600 W Chicago'
        city = 'Chicago'
        state = 'IL'
        zip_code = '60654'
    
    else:
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
        if street_address == '':
            street_address = 'Three Embarcadero Center'
        city = parsed_add['PlaceName'].strip()
        state = parsed_add['StateName'].strip()
        zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://amazon.com/go'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    locs = driver.find_elements_by_css_selector('h4')
    all_store_data = []
    for loc in locs:
        loc_div = loc.find_element_by_xpath('..')
        
        if 'Mon–' in loc_div.text:
            cont = loc_div.text.split('\n')
            
            if len(cont) == 4:
                location_name = cont[0]
                if '30 Rockefeller Plaza' in location_name:
                    street_address, city, state, zip_code = addy_parser(cont[1] + ' ' + cont[2])
                    city = city.replace('Concourse Level,',  '').strip()
                    fixed_loc = cont[3].replace('. Bre', '. \nBre').split('\n')
                    hours = fixed_loc[0]
                    location_type = fixed_loc[1]
                        
                else:
                    street_address, city, state, zip_code = addy_parser(cont[1])
                    hours = cont[2]
                    location_type = cont[3]            
            
            elif len(cont) == 5:
            
                location_name = cont[0]
                if 'Mart' in location_name:
                    street_address, city, state, zip_code = addy_parser(cont[1] + ' ' + cont[2])
                    hours = cont[3]
                    location_type = cont[4]
                else:
                    street_address, city, state, zip_code = addy_parser(cont[1])
                    hours = cont[3]
                    location_type = cont[4]

            elif len(cont) == 3:
                location_name = cont[0]
                street_address, city, state, zip_code = addy_parser(cont[1])
                fixed_loc = cont[2].replace('. Bre', '. \nBre').split('\n')
                hours = fixed_loc[0]
                location_type = fixed_loc[1]
            elif len(cont) == 2:  
                location_name = cont[0]
                loc_fixed = loc_div.text.replace(' Mon–Fri', ' \nMon–Fri').replace('. B', ' .\n B')
                cont = loc_fixed.split('\n')
                street_address, city, state, zip_code = addy_parser(cont[1])
                hours = cont[2]
                location_type = cont[3]
            elif len(cont) == 6:  
                location_name = cont[0]
                street_address, city, state, zip_code = addy_parser(cont[1])
                hours = cont[2] + ' ' + cont[3] 
                location_type = cont[4] + ' ' + cont[5]

            else:
                continue

            country_code = 'US'

            page_url = '<MISSING>'
            longit = '<MISSING>'
            lat = '<MISSING>'
            store_number = '<MISSING>'
            phone_number = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                            store_number, phone_number, location_type, lat, longit, hours, page_url]
            all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
