import csv
import os
from sgselenium import SgSelenium
import json
from fuzzywuzzy import fuzz

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://www.tradefairny.com/' 
    ext = 'store-locations.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    #source = str(driver.page_source.encode("utf-8"))
    ss = driver.find_elements_by_css_selector('script')
    coord_tracker = []
    for s in ss:
        if 'mapbox.generateMap(mapboxDiv' in s.get_attribute('innerHTML'):
            raw_coords = s.get_attribute('innerHTML').split('mapbox.generateMap')[1]
            street_address = raw_coords.split('"')[1].split(',')[0]
            start = raw_coords.find('{')
            end = raw_coords.find('}')
            
            loc = json.loads(raw_coords[start - 1: end + 1].strip().replace(':', ' :').replace(',', ' ,').replace(' ', '"'))
            coord_tracker.append([street_address, loc['lat'], loc['lng']])
    
    locs = driver.find_elements_by_css_selector('div.wsb-element-text')

    all_store_data = []
    for loc in locs:
        cont = loc.text.split('\n')

        if len(cont) != 7:
            continue
        page_url = loc.find_element_by_css_selector('a').get_attribute('href')
        location_name = cont[0]
        store_number = location_name.split('#')[1]
        street_address = cont[1]
        high_score = 0
        lat = ''
        longit = ''
        for coord in coord_tracker:
            score = fuzz.ratio(street_address, coord[0])
            if score > high_score:
                high_score = score
                lat = coord[1]
                longit = coord[2]

        city, state, zip_code = addy_ext(cont[2])
        hours = cont[3]
        phone_number = cont[4].replace('Store Phone:', '').strip()
        
        country_code = 'US'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
     
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
