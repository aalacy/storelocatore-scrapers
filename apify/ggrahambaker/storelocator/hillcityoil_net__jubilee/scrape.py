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

    locator_domain = 'http://hillcityoil.net/jubilee' 
    ext = '/stores.htm'
    r = session.get(locator_domain + ext, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    rows = soup.find('p').find_all('tr')[1:]
    all_store_data = []
    for r in rows:
        cols = r.find_all('td')
        store_number = cols[0].text
        
        location_name = cols[1].text.replace('&amp;', '&')
        
        addy = [l for l in cols[2].prettify().split('\n') if '<' not in l]
        street_address = addy[0].strip().replace('&amp;', '&')
        city, state, zip_code = addy_ext(addy[1].strip())
        phone_number = cols[-1].text.strip()
        if phone_number == '':
            phone_number = '<MISSING>'
            
        if len(phone_number.split('(')) > 1:
            phone_number = phone_number.split('P')[0]        
        
        country_code = "US"
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
