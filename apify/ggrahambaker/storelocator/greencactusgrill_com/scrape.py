import csv
import os
from sgselenium import SgSelenium

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.greencactusgrill.com/'
    ext = 'site-map1.php'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(20)

    loc_links = driver.find_elements_by_xpath('//a[contains(text(),"Green Cactus Grill")]')

    link_list = []
    for link in loc_links:
        url = link.get_attribute('href')
        if url not in link_list:
            link_list.append(url)
    
    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        
        cont = driver.find_element_by_css_selector('div.locationtxt').text.split('\n')
        
        location_name = cont[0]
        street_address = cont[1].strip()
        
        city, state, zip_code = addy_ext(cont[2])
        phone_number = cont[3]
        
        google_href = driver.find_element_by_xpath('//a[contains(@href,"www.google.com/maps/")]').get_attribute('href')
        start = google_href.find('?q=')
        coords = google_href[start + 3: ].split(',')
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link
        hours = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
        #"https://www.google.com/maps/?q=40.8885994,-73.37299347" 
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
