import csv
import json
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

    base_link = "https://urbanbrickspizza.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.71289&max_results=100&search_radius=200&autoload=1"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")
    stores = json.loads(base.text.strip())

    data = []
    locator_domain = "urbanbrickspizza.com"

    for store in stores:
        location_name = "Urban Bricks - " + store["store"]
        street_address = (store["address"] + " " + store["address2"]).strip()
        if "Coming Soon" in street_address:
            continue
        city = store['city']
        state = store["state"]
        if not state:
            state = "<MISSING>"
        zip_code = store["zip"]
        if zip_code == "3009":
            zip_code = "30097"
        country_code = store['country']
        if "States" not in country_code and "Rico" not in country_code:
            continue
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store['phone']
        if not phone:
            phone = "<MISSING>"
        try:
            hours_of_operation = store["hours"].replace("day", "day ").replace("PM", "PM ").strip()
        except:
            hours_of_operation = "<MISSING>"
        latitude = store['lat']
        longitude = store['lng']
        link = store["url"]

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
