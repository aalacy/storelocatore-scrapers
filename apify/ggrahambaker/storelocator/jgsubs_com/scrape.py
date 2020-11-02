import csv
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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'http://www.jgsubs.com/'
    ext = '/locations'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'custom-location-teaser'})

    all_store_data = []
    for loc in locs:
        location_name = loc.find('div', {'class': 'teaser-title'}).text
        
        addy = loc.find('div', {'class': 'teaser-address'}).prettify().split('\n')
        clean_addy = [a.strip() for a in addy if '<' not in a]
        
        street_address = clean_addy[0]
        city, state, zip_code = addy_ext(clean_addy[1])
        
        phone_number = clean_addy[3]
        
        hours = '<MISSING>'

        lat = '<MISSING>'
        longit = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                    store_number, phone_number, location_type, lat, longit, hours, '<MISSING>']

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
