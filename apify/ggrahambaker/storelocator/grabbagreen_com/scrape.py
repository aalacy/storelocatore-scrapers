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

    locator_domain = 'https://www.grabbagreen.com/' 
    ext = 'locator/index.php?brand=34&mode=desktop&pagesize=10000&q=california'

    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'class': 'store'})
    all_store_data = []
    for loc in locs:
        store_number = loc.text.split('#')[1].strip()
        ## check if coming soon
        info_url = 'https://locator.kahalamgmt.com/locator/index.php?mode=infowindow&brand=34&store=' + store_number
        r = session.get(info_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')

        if 'Coming Soon' in soup.find('h1').text:
            continue

        page_url = 'https://www.grabbagreen.com/stores/' + store_number
        r = session.get(page_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        loc_json = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)

        location_name = loc_json['name']
        phone_number = loc_json['telephone'].strip()

        if phone_number == '':
            phone_number = '<MISSING>' 
        addy = loc_json['address']
        
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']
        country_code = 'US'
        
        coords = loc_json['geo']
        lat = coords['latitude']
        longit = coords['longitude']
        hours = loc_json['openingHours'].strip()
        if hours == '':
            hours = '<MISSING>'
        
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
