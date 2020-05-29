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
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    
    locator_domain = 'https://www.sarkujapan.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)

    source = str(driver.page_source)

    coord_dict = {}
    for line in source.splitlines():
        if line.strip().startswith("var marker"):
            clean_line = line.strip()
            if 'var markers = []' in clean_line:
                continue
            if 'var markerID = ' in clean_line:
                continue
            
            coords_start = clean_line.find('[') + 1
            coords_end = clean_line.find(']')
            
            coords = clean_line[coords_start:coords_end].split(',')
            
            id_start = clean_line.find('marker_')
            id_end = clean_line.find('}') - 1

            div_id = clean_line[id_start: id_end]
            
            coord_dict[div_id] =  coords
    
    main = driver.find_element_by_css_selector('ul#locationsResults')
    locs = main.find_elements_by_css_selector('li')
    all_store_data = []
    for loc in locs:
        id_store = loc.find_element_by_css_selector('a').get_attribute('id')
        
        coords = coord_dict[id_store]
        lat = coords[0]
        longit = coords[1]
        
        location_type = loc.find_element_by_css_selector('a').text.replace('\n', ' ')
    
        cont = loc.find_element_by_css_selector('div.wpb_column.vc_column_container.vc_col-sm-4').text.split('\n')
    
        location_name = cont[0]
        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])
        if len(zip_code) == 4:
            zip_code = '0' + zip_code
        phone_number = cont[3].replace('Phone:', '').strip()
        
        hours = loc.find_element_by_css_selector('div.wpb_column.vc_column_container.vc_col-sm-3').text.replace('\n', ' ')
        
        country_code = 'US'
        store_number = '<MISSING>'
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
