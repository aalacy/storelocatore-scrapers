import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.malinandgoetz.com/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=lat&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=40.74777&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bfield%5D=lng&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bvalue%5D=-73.99337&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bfield%5D=store_type&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bfield%5D=store_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bvalue%5D=1&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bfield%5D=region_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=region&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bvalue%5D=6800&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B8%5D%5Bfield%5D=onlyLocation&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B8%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B8%5D%5Bcondition_type%5D=eq&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=30&_=1581111578922'
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.malinandgoetz.com/' 

    r = session.get(url, headers = HEADERS)

    store_json = json.loads(r.content)

    all_store_data = []
    for store in store_json['items']:
        if store['country_id'] != 'US':
            continue
            
        country_code = 'US'
        location_name = store['name']
        store_number = store['region_id']
        state = store['region']
        city = store['city']
        phone_number = store['phone']
        street_address = store['street']
        zip_code = store['postal_code']
        page_url = store['website']
        lat = store['lat']
        longit = store['lng']
        
        r = session.get(page_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        strong_h = soup.find(text=re.compile("(Store Hours|shop hours.)"))
        hours_p = strong_h.parent.parent.parent.find_all('p')
        hours = ''
        for h in hours_p:
            if 'Store Hours' in h.text:
                continue
            
            hours += h.text.replace(',', '') + ', '
   
        hours = hours.replace('shop hours., ', '')
        
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
