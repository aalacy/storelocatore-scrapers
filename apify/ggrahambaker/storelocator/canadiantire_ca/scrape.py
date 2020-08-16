import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
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
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    locator_domain = 'https://www.canadiantire.ca/'
    url = 'https://api-triangle.canadiantire.ca/dss/services/v4/stores?lang=en&radius=1000000&maxCount=1000&lat=43.653226&lng=-79.3831843&storeType=store'

    r = session.get(url, headers = HEADERS)
    locs = json.loads(r.text)
    all_store_data = []
    for loc in locs:
        location_name = loc['storeName']
        store_number = loc['storeNumber']
        street_address = loc['storeAddress1'] + ' ' + loc['storeAddress2']
        state = loc['storeProvince']
        city = loc['storeCityName']
        zip_code = loc['storePostalCode']
        lat = loc['storeLatitude']
        longit = loc['storeLongitude']
        phone_number = loc['storeTelephone']
        location_type = loc['storeType']
        
        try:
            hours_obj = loc['workingHours']['general']
            hours = ''
            for h in hours_obj:
                hours += h + ' ' + hours_obj[h] + ' '
        except:
            hours = '<MISSING>'
            
        page_url = '<MISSING>'

        country_code = 'CA'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
