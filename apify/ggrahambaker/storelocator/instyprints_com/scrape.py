import csv
import os
from sgrequests import SgRequests
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
    locator_domain = 'https://www.instyprints.com/'
    ext = 'locations.json'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    store_data = json.loads(page.content)['serviceAreas']['serviceArea']

    all_store_data = []
    for store in store_data:
        hours = ''
        for day, o_c in store['_hours'].items():

            hours += day + ' '
            open_time = o_c['o']
            close_time = o_c['c']
            if open_time == 'Closed':
                hours += open_time + ' '
                continue

            hours += open_time + ' - ' + close_time + ' '

        location_name = store['_name']
        street_address = store['_address'].replace('<br/>', ' ')
        city = store['_city']
        state = store['_state']
        zip_code = store['_zip']
        phone_number = store['_phone']
        page_url = store['_url']
        lat = store['_lat']
        longit = store['_lng']

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        print(store_data)
        print()
        all_store_data.append(store_data)
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
