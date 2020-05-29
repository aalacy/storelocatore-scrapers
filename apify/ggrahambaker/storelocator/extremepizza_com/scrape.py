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

def fetch_data():
    locator_domain = 'https://www.extremepizza.com/' 
    ext = 'store-locator/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.locationListItem')
    all_store_data = []
    for loc in locs:
        location_name = loc.find_element_by_css_selector('h3').text
        page_url = loc.find_element_by_css_selector('a').get_attribute('href')
        hours = loc.find_element_by_css_selector('div.locationListItemHours').text.replace('ORDER ONLINE', '').strip().replace('\n', ' ')
        
        if 'Coming Soon' in hours:
            continue
        if 'Coming soon' in hours:
            continue
        spans = loc.find_elements_by_css_selector('span')
        addy = spans[0].text.split(',')
        
        street_address = addy[0].strip()
        city = addy[-2].strip()
        state_zip = addy[-1].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
        
        google_map = spans[0].find_element_by_css_selector('a').get_attribute('href')
        
        start = google_map.find('query=')
        end = google_map.find('&query_place')
        coords = google_map[start + 6: end].split(',')
        if len(coords) == 2:
            lat = coords[0]
            longit = coords[1]
        else:
            lat, longit = '<MISSING>', '<MISSING>'
        phone_number = spans[1].text

        country_code = 'US'
        store_number = '<MISSING>'
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
