import csv
import json
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

    base_link = "https://us.brandymelville.com/locations"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")

    all_scripts = base.find_all('script')
    for script in all_scripts:
        if "locations =" in str(script):
            script = str(script)
            break

    js = script.split("locations =")[1].split("}}")[0].strip() + "}}"
    store_data = json.loads(js)

    data = []
    locator_domain = "brandymelville.com"

    for country in store_data:
        if country not in ["Canada","United States"]:
            continue

        states = store_data[country]
        for state in states:
            stores = states[state]
            for store in stores:
                location_name = "<MISSING>"
                street_address = store[1]

                digit = re.search("\d", street_address).start(0)
                if digit != 0:
                    street_address = street_address[digit:]

                city = store[0]
                zip_code = "<MISSING>"
                if "5644 Bay Street, Emeryville" in street_address:
                    street_address = "5644 Bay Street"
                    zip_code = "94608"
                if country == "Canada":
                    country_code = "CA"
                else:
                    country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                phone = store[2]
                if not phone:
                    phone = "<MISSING>"
                hours_of_operation = store[-1]
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                link = "<MISSING>"

                # Store data
                data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()