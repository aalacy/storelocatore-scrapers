import csv
import os
from sgselenium import SgSelenium
import re
import usaddress

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
    
    if 'PlaceName' in parsed_add:
        city = parsed_add['PlaceName']
    else:
        city = '<MISSING>'
    
    if 'StateName' in parsed_add:
        state = parsed_add['StateName']
    else:
        state = '<MISSING>'
        
    if 'ZipCode' in parsed_add:
        zip_code = parsed_add['ZipCode']
    else:
        zip_code = '<MISSING>'

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
    locator_domain = 'http://unclelouiegee.com/'
    ext = 'locations/?wpbdp_view=all_listings'

    driver = SgSelenium().chrome()

    driver.get(locator_domain + ext)
    not_done = True
    all_store_data = []
    while not_done:
        titles = driver.find_elements_by_css_selector('div.listing-title')
        conts = driver.find_elements_by_css_selector('div.excerpt-content')
        
        for i, title in enumerate(titles):
            
            addy = title.text.replace('-', '').replace('–', '')
            if 'Coming Soon' in addy:
     
                continue
            if '(' in addy:
                addy = addy.split('(')[0]
            if ':' in addy:
                addy = addy.split(':')[1]
                
            addy = addy.strip()
            get_more_info = False
            
            if 'Oceanside NY' in addy:
                street_address = '<MISSING>'
                city = 'Oceanside'
                state = 'NY'
                zip_code = '<MISSING>'
                phone_number = '516 279 9412'
            elif '107 Commercial Blvd.' in addy:
                street_address = '107 Commercial Blvd.'
                city = 'Ft. Lauderdale'
                state = 'FL'
                zip_code = '33308'
            else:
                codes = re.findall('\d{5}$', addy)
                
                if len(codes) == 0:
                    
                    if len(addy.strip().split(' ')) < 4:
                        get_more_info = True

                if not get_more_info:
                    street_address, city, state, zip_code = parse_address(addy)

                phone_number = ''
                cont = conts[i].text.split('\n')
                for c in cont:
                    if 'Business Phone Number:' in c:

                        phone_number = c.split(':')[1].strip()

                    if 'About Our Store:' in c:
                        if get_more_info:
                            
                            values = conts[i].find_elements_by_css_selector('span.value')
                            for v in values:

                                codes = re.findall('\d{5}$', v.text)
                           
                                if 'SATELITE LOCATION' in v.text:
                                    street_address = '<MISSING>'
                                    city = 'Sebastian'
                                    state = 'Florida'
                                    zip_code = '32958'

                                else:
                                    if len(codes) == 1:
                                        street_address, city, state, zip_code = parse_address(v.text)

            if phone_number == '':
                phone_number = '<MISSING>'
            location_name = '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            hours = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            page_url = '<MISSING>'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
        
        next_span = driver.find_element_by_css_selector('span.next')
        a_tags = next_span.find_elements_by_css_selector('a')
        if len(a_tags) == 1:
            next_span.click()
            driver.implicitly_wait(5)
            
        else:
            not_done = False
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
