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
    locator_domain = 'http://qolhs.org/'
    ext = 'locations/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#shailan-subpages-2')

    links_raw = main.find_elements_by_css_selector('a')

    links = [a.get_attribute('href') for a in links_raw]

    all_store_data = []
    for link in links:
        if '/quality-health-express/' in link:
            continue
        driver.get(link)
        cols = driver.find_element_by_css_selector('article').find_elements_by_css_selector('div.col-md-6')
        
        addy = cols[0].text.split('\n')
        
        location_name = addy[0]
        street_address = addy[1]
        city, state, zip_code = addy_ext(addy[2])
        phone_number = addy[3]
        
        hours = cols[1].text.replace('\n', ' ')

        google = driver.find_element_by_css_selector('iframe').get_attribute('src')
        start = google.find('center=')
        coords = google[start + 7:].split(',')
        lat = coords[0]
        longit = coords[1].split('&zoo')[0]    

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
