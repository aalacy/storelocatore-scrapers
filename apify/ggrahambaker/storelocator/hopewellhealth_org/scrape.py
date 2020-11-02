import csv
import os
from sgselenium import SgSelenium

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
    locator_domain = 'http://www.hopewellhealth.org/' 
    ext = 'locations.htm'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('table.content')

    dup_tracker = []
    all_store_data = []
    for loc in locs:
        cols = loc.find_elements_by_css_selector('td')
        for col in cols:
            info_raw = col.text.split('\n')
            if len(info_raw) == 1:
                continue
            info = []
            for i in info_raw:
                if 'Formerly' in i:
                    continue
                if i == '':
                    continue
                if 'Perry County WIC Program' in i:
                    continue
    
                info.append(i)
  
            location_name = info[0]
            if '2541 Panther Drive' in location_name:
                continue
            if 'New Lexington' in location_name:
                off = 1
            else:
                off = 0
            street_address = info[1 + off]
            if street_address not in dup_tracker:
                dup_tracker.append(street_address)
            else:
                continue
            city, state, zip_code = addy_ext(info[2 + off])
            phone_number = info[3 + off].split(':')[1].split('or')[0].strip()
            
            link = col.find_element_by_css_selector('a').get_attribute('href')
            
            start = link.find('sll=')
            if start > 0:
                coords = link[start + 4:].split(',')
                lat = coords[0]
                longit = coords[1].split('&')[0]
            else:
                start = link.find('@')
                if start > 0:
                    coords = link[start + 1:].split(',')
                    lat = coords[0]
                    longit = coords[1]
                else:
                    lat, longit = '<MISSING>', '<MISSING>'
                
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'

            hours = '<MISSING>'
            page_url = '<MISSING>'
            street_address = street_address.split('Suite')[0].strip().split('Unit')[0].strip().replace(',', '').strip()

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
       
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
