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
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://choiceoneuc.com/'
    ext = 'locations'

    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find_all('div', {'class': 'views-field'})

    loc_dict = {}
    for line in soup.prettify().split('\n'):
        if line.startswith('addelement('):
            info = line.strip().replace('addelement(', '').replace("'",'').split(',')
            loc_dict[info[2].strip()] = [info[0], info[1].strip()]
            
    dup_tracker = []
    all_store_data = []
    for loc in locs:
        location_name = loc.find('h3').text
        if location_name not in dup_tracker:
            dup_tracker.append(location_name)
        else:
            continue
            
        lat = loc_dict[location_name][0]
        longit = loc_dict[location_name][1]
            
        hours_raw = loc.find('div', {'class': 'office-hours__item'}).text
        hours = ' '.join(hours_raw.split())
        
        addy_raw = loc.find('div', {'class': 'field--name-field-display-address'}).prettify().split('\n')

        addy = [a for a in addy_raw if '<' not in a]
        if len(addy) > 3:
            addy = addy[1:]
        
        street_address = addy[0].strip()
        
        city, state, zip_code = addy_ext(addy[1].strip())
        
        phone_number = loc.find('a', {'class': 'phone-link'}).text
        
        page_url = loc.find('a', {'class': 'btn-alert'})['href']
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
