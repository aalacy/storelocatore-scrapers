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

    locator_domain = 'https://www.roseoilco.com/landl-stores' 

    r = session.get('https://www.roseoilco.com/rosemart-stores', headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')

    all_store_data = []
    for row in rows[1:]:
        location_name = row.find('th').text.replace(':', '')
        if 'L&L' not in location_name:
            continue
        
        addy = row.find('td').text.split(',')
        street_address = addy[0]
        if len(addy) == 4:
            off = 1
        else:
            off = 0

        city = addy[1 + off].strip()
        state = addy[2 + off].strip()
        zip_code = '<MISSING>'
        phone_number = '252-438-7141'
        country_code = 'US'
        store_number = '<MISSING>'
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
