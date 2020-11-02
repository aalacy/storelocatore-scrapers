import csv
import json
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://kwikshop.com/StoreData/GetStoreDataByLocation?location=10.6333%2C-61.3667&currentPageId=3038"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")
    stores = json.loads(base.text.strip())

    data = []
    locator_domain = "kwikshop.com"

    for store in stores:
        location_name = "Kwik Shop - " + store["City"]
        street_address = store["Address"]
        city = store['City']
        state = store["State"]
        zip_code = store["Zip"]
        country_code = "US"
        store_number = store["StoreId"]
        location_type = "<MISSING>"
        phone = store['Phone']
        hours_of_operation = "<MISSING>"
        latitude = store['Latitude']
        longitude = store['Longitude']
        link = "https://kwikshop.com/store-locator/"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()