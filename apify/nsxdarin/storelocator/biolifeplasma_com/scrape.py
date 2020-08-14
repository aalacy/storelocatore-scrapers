import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.biolifeplasma.com/us/resources/center/centers-with-additional-info'
    r = session.get(url, headers=headers)
    website = 'biolifeplasma.com'
    country = 'US'
    items = json.loads(r.content)
    for item in items:
        add = item['addressLine1']
        city = item['city']
        name = item['alias']
        store = item['id']
        lat = item['latitude']
        lng = item['longitude']
        state = item['state']['code']
        zc = item['zipCode']
        loc = 'https://www.biolifeplasma.com/us/donation-center?centerId=' + str(store)
        phone = item['phoneNumber']
        typ = '<MISSING>'
        hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
