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

    locator_domain = 'https://www.willamettegraystone.com/' 
    ext = 'where-to-buy.php'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find('div', {'class': 'branches-list'}).find_all('div', {'class': 'b-address'})

    all_store_data = []
    for loc in locs:
        location_name = loc.find('h3').text
        addy = loc.find('p').prettify().split('\n')
        info = []
        for a in addy:
            if '<' in a:
                continue
            if a.strip() == '':
                continue
            info.append(a.strip())

        street_address = info[0]
        if 'PO Box' in info[1]:
            off = 1
        else:
            off = 0
        city, state, zip_code = addy_ext(info[1 + off])
        phone_number = info[2 + off].replace('Phone:', '').strip()
        hours = ''

        for h in info[3 + off:]:
            if 'Fax' in h:
                continue
            hours += h + ' '
            
        hours = hours.replace('&amp;', '&').replace('Hours:', '').strip()
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
