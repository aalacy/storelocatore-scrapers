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

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.elcompadrerestaurant.com/' 
    ext = 'locations'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all('div', {'id': 'ctl01_pSpanDesc'})

    locations = locs[0].find_all('td')
    hours = locs[1].text.strip()
    all_store_data = []
    for l in locations:
        location_name = l.find('h6').text
        addy_split = l.find('p', {'class': 'fp-el'}).prettify().split('\n')
        
        for a in addy_split:
            if '<' in a:
                continue
            if 'Phone' in a:
                phone_number = a.replace('Phone.', '').strip()
                continue
            addy = a.split(',')
        
        street_address = addy[0]
        city = addy[1].strip()
        state_zip = addy[2].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
