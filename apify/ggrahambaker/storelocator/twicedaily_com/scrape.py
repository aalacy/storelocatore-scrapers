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
    locator_domain = 'https://twicedaily.com/'
    ext = 'location/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, '/regions/')]")
    state_links = []
    
    for h in hrefs:
        link = h.get_attribute('href')

        if link not in state_links:
            state_links.append(link)

    all_store_data = []
    for state in state_links:
        driver.get(state)
        
        driver.implicitly_wait(10)

        next_page = driver.find_elements_by_xpath("//a[contains(text(),'Next Page')]")
        if len(next_page) == 1:
            next_page_link = next_page[0].get_attribute('href')
            state_links.append(next_page_link)

        locs = driver.find_elements_by_css_selector('article')
        
        for loc in locs:
            page_url = loc.find_element_by_css_selector('a.entry-title-link').get_attribute('href')
            location_name = loc.find_element_by_css_selector('a.entry-title-link').text
            js_map = loc.find_element_by_css_selector('button.btn.btn-red.btn-dir').get_attribute('onclick')
            google_link = js_map.split("'")[1]
            start = google_link.find('dir/')
            if start > 0:
                coords = google_link[start + 4: ].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

            cont = loc.find_element_by_css_selector('table').text.split('\n')
            street_address = cont[0]
            city, state, zip_code = addy_ext(cont[1])
            phone_number = cont[2]

            hours = 'Open 24 / 7'
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
