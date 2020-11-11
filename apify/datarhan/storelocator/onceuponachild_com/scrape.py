import csv
import json
import usaddress
from lxml import etree

from sgrequests import SgRequests

DOMAIN = 'onceuponachild.com'


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []
    gathered_ids = []
    
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

    canada_states = [
        'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'
    ]

    states += canada_states
    for state in states:
        state_url = 'https://wmrk-api.treefort.com/corp/ouac/locations/search/{}?maxDistance=500'.format(state)
        state_response = session.get(state_url)
        state_data = json.loads(state_response.text)
        if not state_data:
            continue
        
        for store_data_countries in state_data[0]['countries']:
            for store_data_regions in store_data_countries['regions']:
                for store_data in store_data_regions['stores']:
                    if store_data['statusText'] == 'Coming Soon':
                        continue
                    store_url = 'https://onceuponachild.com/locations?query={}'.format(state)
                    location_name = store_data['storeName']
                    street_address = store_data['addressLine1']
                    if street_address:
                        if store_data['addressLine2']:
                            street_address += ' ' + store_data['addressLine2']
                    if not street_address:
                        street_address = store_data['addressLine2']
                    street_address = street_address if street_address else '<MISSING>'
                    city = store_data['city']
                    city = city if city else '<MISSING>'
                    state = store_data['region']
                    state = state if state else '<MISSING>'
                    zip_code = store_data['postalCode']
                    zip_code = zip_code if zip_code else '<MISSING>'
                    if zip_code.startswith('CA'):
                        zip_code = zip_code[2:]
                    country_code = store_data['countryCode']
                    country_code = country_code if country_code else '<MISSING>'
                    store_number = store_data['storeNumber']
                    phone = store_data['phoneNumber']
                    phone = phone if phone else '<MISSING>'
                    location_type = '<MISSING>'
                    latitude = store_data['latitude']
                    latitude = latitude if latitude else '<MISSING>'
                    longitude = store_data['longitude']
                    longitude = longitude if longitude else '<MISSING>'
                    hours_of_operation = store_data['storeHours']
                    hours_of_operation = hours_of_operation if hours_of_operation else '<MISSING>'
                    
                    item = [
                        DOMAIN,
                        store_url,
                        location_name,
                        street_address,
                        city,
                        state,
                        zip_code,
                        country_code,
                        store_number,
                        phone,
                        location_type,
                        latitude,
                        longitude,
                        hours_of_operation
                    ]
                    if store_number not in gathered_ids:
                        gathered_ids.append(store_number)
                        items.append(item)
            
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
