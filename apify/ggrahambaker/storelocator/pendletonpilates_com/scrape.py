import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain = 'http://www.pendletonpilates.com/'
    ext = 'new-page-1'

    to_scrape = locator_domain + ext

    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    json_data = json.loads(soup.find('div', {'class': 'sqs-block'})['data-block-json'])

    lat = json_data['location']['markerLat']
    longit = json_data['location']['markerLng']
    location_name=json_data['location']['addressTitle']
    street_address = json_data['location']['addressLine1']
    addr = (json_data['location']['addressLine2']).split(',')
    city = addr[0]
    state = addr[1]
    zip_code = addr[2]
    phone_number = '<MISSING>'
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    hours = '<MISSING>'

    store_data = [[locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]]
    return store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
