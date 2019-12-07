import csv
import requests
import usaddress
import us
from uszipcode import SearchEngine
from pypostalcode import PostalCodeDatabase

search = SearchEngine(simple_zipcode=True)
pcdb = PostalCodeDatabase()

API_URL = 'https://world.maxmara.com/store-locator?south=-81.96490562901019&west=-174.52175505623518&north=87.18732610733203&east=39.93136994376482&lat=40.7127431&lng=-74.01337949999999&name=&listJson=true&withoutRadius=false'
COUNTRY_DICT = { 'United States': 'US', 'Canada': 'CA', 'united states': 'US', 'canada': 'CA' }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    stores = []
    response = requests.get(API_URL)
    data = response.json()
    for store in data['features']:
        country = store['properties']['country']
        if country not in COUNTRY_DICT:
            continue
        country_code =COUNTRY_DICT[country]
        locator_domain = 'https://world.maxmara.com/'
        city = store['properties']['city']
        location_name = store['properties']['displayName']
        zip_code = store['properties']['zip']
        store_number = store['properties']['name']
        latitude = store['properties']['lat']
        longitude = store['properties']['lng']
        hours_of_operation = store['properties']['openingHours']
        phone = store['properties']['phone1']
        full_address = store['properties']['formattedAddress']
        tagged = usaddress.tag(full_address)[0]
        street_address = tagged['AddressNumber']+" "+tagged['StreetName']+" "+tagged['StreetNamePostType']
        prov = store['properties']['prov']
        state = prov.split('-')[1] if prov else '<MISSING>'
        zip_lookup = search.by_zipcode(zip_code).to_dict()
        if country_code == 'US' and 'state' in zip_lookup:
            state = zip_lookup['state']
        elif country_code == 'CA':
            location = pcdb[zip_code[0:3]]
            state = location.province
        page_url = '<MISSING>'
        location_type = '<MISSING>'
        stores.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return stores

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
