import csv
import os
from sgselenium import SgSelenium
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
    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']

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
    locator_domain = 'https://www.navarro.com/'
    next_link = 'store-locator.htm'

    driver = SgSelenium().chrome()
   
    still_scrolling = True

    all_store_data = []
    dup_tracker = []
    while still_scrolling:
        driver.get(locator_domain + next_link)
        driver.implicitly_wait(5)
        
        locs = driver.find_element_by_css_selector('div#location_rightside').find_elements_by_css_selector('div')
        
        for loc in locs:
            on_click = loc.find_elements_by_css_selector('span')
            if len(on_click) == 0:
                on_click = loc.find_elements_by_css_selector('button')
            
            google_click_info = on_click[0].get_attribute('onclick')
            
            start = google_click_info.find("('")
            
            coords = google_click_info[start + 2:].split(',')
            
            lat = coords[0]
            longit = coords[1].replace("'",'').strip()
            
            off = 0
            cont = loc.text.split('\n')

            location_name = cont[0].strip()
            if location_name not in dup_tracker:
                dup_tracker.append(location_name)
            else:
                continue
            if 'AIRPORT' in location_name:
                street_address, city, state, zip_code = parse_address(cont[1] + ' ' + cont[2])
                off = 1
            else:
                street_address, city, state, zip_code = parse_address(cont[1])
            
            phone_number = cont[2 + off].replace('STORE:', '').strip()
            
            hours = ''
            for c in cont[3 + off:]:
                if 'PHARMACY' in c:
                    break
            
                hours += c + ' '
            
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            page_url = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
        
        nexts = driver.find_elements_by_xpath('//span[contains(text(),"Next")]')
        
        if len(nexts) == 1:
            href = nexts[0].find_element_by_xpath('../..').get_attribute('onclick')
            next_link = href.split("'")[1]
        else:
            still_scrolling = False
            continue
            
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
