import csv
import os
from sgselenium import SgSelenium
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.harmondiscount.com/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    driver.implicitly_wait(10)

    url = 'https://www.harmondiscount.com/api/commerce/storefront/locationUsageTypes/SP/locations/?startIndex=0&pageSize=500'

    driver.get(url)
    driver.implicitly_wait(10)

    locs = json.loads(driver.find_element_by_css_selector('body').text)['items']

    all_store_data = []
    for loc in locs:
        if 'Harmon' in loc['locationTypes'][0]['name']:
            location_name = loc['name']
            
            street_address = loc['address']['address1']
            
            city = loc['address']['cityOrTown']
            state = loc['address']['stateOrProvince']
            zip_code = loc['address']['postalOrZipCode']
            
            if 'USA' in loc['address']['postalOrZipCode']:
                country_code = 'US'
            else:
                country_code = 'CA'
                
            coords = loc['geo']
            
            lat = coords['lat']
            longit = coords['lng']
            
            phone_number = loc['phone']
            
            hours = ''
            
            hours_obj = loc['regularHours']
            for day, val in hours_obj.items():
                
                if val['label'] == '':
                    hours = '<MISSING>'
                    break
                    
                hours += day + ' ' + val['label'] + ' '
                
            store_number = '<MISSING>'
            location_type = '<MISSING>'
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
