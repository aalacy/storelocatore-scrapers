import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    url = 'https://tacomac.com/wp-admin/admin-ajax.php?action=store_search&lat=33.7845409&lng=-84.3489467&max_results=500&radius=500'

    locator_domain = 'https://tacomac.com/' 
    r = session.get(url, headers = HEADERS)

    locs = json.loads(r.content)

    all_store_data = []
    for loc in locs:
        location_name = loc['store']
        store_number = loc['id']
        street_address = loc['address'] + ' ' + loc['address2']
        street_address = street_address.strip() 
        city = loc['city']
        state = loc['state']
        zip_code = loc['zip']
        lat = loc['lat']
        longit = loc['lng']
        
        phone_number = loc['phone']
        
        tds = BeautifulSoup(loc['hours'], 'html.parser').find_all('td')
        hours = ''
        for td in tds:
            hours += td.text + ' '
            
        country_code = 'US'
        location_type = '<MISSING>'
        page_url = loc['permalink']
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
