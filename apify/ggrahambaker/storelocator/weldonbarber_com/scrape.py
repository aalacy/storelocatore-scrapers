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
    locator_domain = 'https://weldonbarber.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    locs = driver.find_elements_by_css_selector('div.wpb-column.wpb-col-4')

    link_list = []
    for loc in locs:
        icons = loc.find_elements_by_css_selector('div.ico')
        if len(icons) > 0:
            link = icons[1].find_element_by_css_selector('a').get_attribute('href')
        
            link_list.append(link)
    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        location_name = driver.find_elements_by_css_selector('h1')[1].text
        cols = driver.find_elements_by_css_selector('div.wpb-column.wpb-col-4')
        hours = cols[0].text.replace('SHOP HOURS', '').replace('\n', ' ').strip()
        
        addy = cols[1].text.split('\n')[2:]
        if len(addy) == 4:
            street_address = addy[0] + ' ' + addy[1]
            off = 1
        else:
            street_address = addy[0]
            off = 0
            
        city, state, zip_code = addy_ext(addy[1 + off])
        dir_link = cols[1].find_element_by_css_selector('a').get_attribute('href')
        start = dir_link.find('@')
        if start < 0:
            start = dir_link.find('?ll')
            if start < 0:
                lat = '<MISSING>'
                longit = '<MISSING>'
            else:
                end = dir_link.find('&z')
                coords = dir_link[start + 4: end].split(',')
                lat = coords[0]
                longit = coords[1]

        else:
            coords = dir_link[start + 1:].split(',')[:2]
            lat = coords[0]
            longit = coords[1]

        phone_number = cols[2].text.split('\n')[2].replace('+1', '').strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, link]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
