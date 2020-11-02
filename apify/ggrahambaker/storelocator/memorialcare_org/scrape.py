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

    locator_domain = 'https://www.memorialcare.org/' 
    ext = 'api/location-search-lookup?&proximity[value]=25'
    r = session.get(locator_domain + ext, headers = HEADERS)

    locs = json.loads(r.content)
    all_store_data = []
    for loc in locs:
        store_number = loc['id']
        page_url = locator_domain[:-1] + loc['url']

        location_type = loc['location_type'].replace('&amp;', '&').strip()
        if location_type == '':
            location_type = '<MISSING>'
        lat = loc['lat']
        longit = loc['lon']
        
        location_name = loc['title']
        
        street_address = loc['address_line_1']
        
        street_address = street_address.strip()
        city = loc['city']
        state = loc['state']
        zip_code = loc['zip']
        
        country_code = 'US'
        
        hours = '<MISSING>'
        
        r = session.get(page_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        ps = soup.find_all('p', {'class': 'location-marquee__info'}) #location-marquee__info--has-image
        for p in ps:
            if 'Phone' in p.text:
                phone_number = p.text.replace('Phone:', '').strip()

        try:
            hours = ''
            hours_p = soup.find('div', {'class': 'open-hours__description'}).find_all('p')
            for h in hours_p:
                hours += h.text + ' '
                
            hours = hours.split('Lab Hours')[0]
            hours = hours.split('Holiday Hours')[0]
            
            hours = ' '.join(hours.split())
            
        except:
            hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
