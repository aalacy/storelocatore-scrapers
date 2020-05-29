import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://code3er.com/'

    url = 'https://code3er.com/wp-admin/admin-ajax.php?action=store_search&lat=33.179969&lng=-96.69589400000001&max_results=25&search_radius=500&autoload=1'
    page = session.get(url)
    assert page.status_code == 200
    loc_json = json.loads(page.content)

    all_store_data = []
    for loc in loc_json:
        location_name = loc['store'].replace('&#8211;', '').strip()
        street_address = loc['address'] + ' ' + loc['address2']
        city = loc['city'].replace(',', '')
        state = loc['state']
        zip_code = loc['zip']
        country_code = 'US'
        lat = loc['lat']
        longit = loc['lng']
        phone_number = loc['phone']
        
        days = BeautifulSoup(loc['hours'], 'html.parser').find_all('td')
        hours = ''
        for day in days:
            hours += day.text + ' '

        store_number = '<MISSING>'
        location_type = ''
        if 'ER' in location_name or 'Emergency Room' in location_name:
            location_type += 'ER '
        if 'Urgent Care' in location_name:
            location_type += 'Urgent Care '
            
        location_type = location_type.strip()
        page_url = '<MISSING>'
            
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
