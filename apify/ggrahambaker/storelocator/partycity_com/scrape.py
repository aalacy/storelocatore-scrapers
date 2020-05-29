import csv
import os
from sgselenium import SgSelenium
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.partycity.com/'
    url = 'https://stores.partycity.com/'

    driver = SgSelenium().chrome()
    driver.get(url)

    driver.implicitly_wait(10)

    country_links = []

    for country in driver.find_elements_by_css_selector('a.gaq-link'):
        if '#' in country.get_attribute('href'):
            country_links.append(country.get_attribute('href'))

    state_list = []
    for country in country_links:
        driver.get(country)
        driver.implicitly_wait(10)
        
        main = driver.find_element_by_css_selector('div.tlsmap_list')
        states = main.find_elements_by_css_selector('a.gaq-link')
        for state in states:
            state_list.append(state.get_attribute('href'))
        
    city_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        
        main = driver.find_element_by_css_selector('div.map-list')
        cities = main.find_elements_by_css_selector('a.gaq-link')

        for city in cities:
            city_list.append(city.get_attribute('href'))
            
    link_list = []

    for city in city_list:
        driver.get(city)
        driver.implicitly_wait(10)
        
        locs = driver.find_elements_by_css_selector('div.address')
        for loc in locs:
            link = loc.find_element_by_css_selector('a').get_attribute('href')
            link_list.append(link)

    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    session = SgRequests()

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        split = link.split('/')
        country_code = split[3].upper()
        
        info = soup.find('script', {'type': 'application/ld+json'}).text
        loc = json.loads(info)[0]

        addy = loc['address']
        
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']
        
        phone_number = addy['telephone']
        
        coords = loc['geo']
        lat = coords['latitude']
        longit = coords['longitude']
        
        hours = loc['openingHours']
        
        location_name = loc['mainEntityOfPage']['headline']
        
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
