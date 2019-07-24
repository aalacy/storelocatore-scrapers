import csv
import requests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

## generalize scraping for each url
def scrape_url(page, all_store_data, locator_domain):
    soup = BeautifulSoup(page.content, 'html.parser')
    stores = soup.find_all('div', {'class': 'location-content'})
    for store in stores:
        location_name = store.find('a').text.strip()
        addy_info = store.find('p').text.strip().split('\n')
    
        street_address = addy_info[0].strip()
        
        city = addy_info[1].split('\xa0')[0].strip()[:-8].strip()
        state_zip = addy_info[1].split('\xa0')[0].strip()[-8:].split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
        
        phone_number = addy_info[3]
        
        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        store_number = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        
    
def fetch_data():
    locator_domain = 'https://www.perfectlooksalons.com/' 

    ext_arr = ['/family-haircare/alaska/', 'family-haircare/arizona/', 'family-haircare/idaho/', 'family-haircare/oregon/', 'family-haircare/washington/']

    all_store_data = []
    for ext in ext_arr:
        to_scrape = locator_domain + ext
        page = requests.get(to_scrape)
        assert page.status_code == 200

        scrape_url(page, all_store_data, locator_domain)
        

    

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
