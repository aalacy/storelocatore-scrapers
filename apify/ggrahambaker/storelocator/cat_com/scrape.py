import csv
from sgrequests import SgRequests
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=5000&searchDistance=5000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7%2C2&serviceId=1%2C2%2C3%2C4%2C8%2C9%2C10%2C5%2C6%2C7%2C12&appId=n6HDEnXnYRTDAxFr&searchValue=-122.3215448%2C47.6338217'

    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    r = session.get(url, headers = HEADERS)
    locs = json.loads(r.content)

    dup_tracker = set()
    locator_domain = 'https://www.cat.com/'
    all_store_data = []
    for loc in locs:
        
        if not (loc['countryCode'] == 'CA' or loc['countryCode'] == 'US'):
            continue
        if loc['isSubDealer']:
            continue
            
        location_name = loc['dealerLocationName'].strip()
        if location_name not in dup_tracker:
            dup_tracker.add(location_name)
        else:
            continue
            
        street_address = loc['siteAddress'] + ' ' + loc['siteAddress1']
        street_address = street_address.strip()
        city = loc['siteCity']
        state = loc['siteState']
        zip_code = loc['sitePostal']
        country_code = loc['countryCode']
        
        store_number = loc['dealerLocationId']
        
        if loc['locationPhone'] == None or loc['locationPhone'].strip() == '':
            phone_number = '<MISSING>' 
        else:
            phone_number = loc['locationPhone']

        location_type = loc['type']

        lat = loc['latitude']
        longit = loc['longitude']
        
        hours_json = loc['stores'][0]
        
        hours = hours_json['storeHoursMon'] + ' ' + hours_json['storeHoursTue'] + ' ' + hours_json['storeHoursWed'] + ' '
        hours += hours_json['storeHoursThu'] + ' ' + hours_json['storeHoursFri'] + ' ' + hours_json['storeHoursSat'] + ' '
        hours += hours_json['storeHoursSun']
        hours = hours.strip()
        
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
