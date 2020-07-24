import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://originalchopshop.com/'
    ext = 'restaurant-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    #main = driver.find_element_by_css_selector('section.bg-light-beige.torn-edge-after')
    locations = driver.find_elements_by_css_selector('div.location')
    all_store_data = []
    for loc in locations:
        content = loc.text.split('\n')
        location_name = content[0]
        phone_number = content[1]
        street_address = content[2]
        #print(content[3])
        try:
            city, state, zip_code = addy_ext(content[3])
        except:
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = '<MISSING>'
            
        hours = ''
        for h in content[6:]:
            hours += h + ' '
        try:
            href = loc.find_element_by_css_selector('a').get_attribute('href')
            start_idx = href.find('/@')
            end_idx = href.find('z/data')
            if start_idx > 0:
                coords = href[start_idx + 2:end_idx].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'
        except:
            lat = '<MISSING>'
            longit = '<MISSING>'
            

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        if len(hours) < 2:
            hours = '<MISSING>'

        store_data = [locator_domain,locator_domain+ext, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
