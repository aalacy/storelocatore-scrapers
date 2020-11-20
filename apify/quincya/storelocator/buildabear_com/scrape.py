import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://www.buildabear.com/on/demandware.store/Sites-buildabear-us-Site/default/Stores-GetNearestStores?latitude=36.1835287&longitude=-95.9660485&countryCode=US&distanceUnit=mi&maxdistance=10000"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()['stores']

    data = []
    locator_domain = "buildabear.com"

    for store_id in stores:
        store = stores[store_id]
        location_name = store["name"]
        street_address = (store["address1"] + " " + store["address2"]).strip()
        city = store['city']
        state = store["stateCode"]
        zip_code = store["postalCode"]
        country_code = store["countryCode"]
        if country_code not in ["US","CA"]:
            continue
        store_number = store_id
        location_type = "<MISSING>"
        phone = store['phone']

        if "closed" in location_name.lower():
            hours_of_operation = "Closed"
        else:
            hours_of_operation = ""
            raw_hours = store["storeHours"]
            hours = list(BeautifulSoup(raw_hours,"lxml").stripped_strings)
            for hour in hours:
                if "hours" not in hour.lower():
                    hours_of_operation = (hours_of_operation + " " + re.sub(', .+: ', ' ', hour)).strip()

        latitude = store['latitude']
        longitude = store['longitude']
        link = "https://www.buildabear.com/locations?StoreID=" + store_id

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
