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

    session = SgRequests()

    api_link = "https://cdn.shopify.com/s/files/1/0044/5877/4577/t/2/assets/stores.json?v=12088630757016997992"
    base_link = "https://www.triohockey.ca/pages/stores"

    req = session.get(api_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    stores = json.loads(base.text.strip())["data"]

    data = []
    locator_domain = "triohockey.ca"

    for store in stores:
        location_name = store["name_en"]
        street_address = store["address1_en"]
        city = store['city']
        state = store["province"]
        zip_code = store["postal_code"]
        country_code = "CA"
        store_number = store["store_number"]
        location_type = "<MISSING>"
        phone = store["telephone"]
        latitude = store['latitude']
        longitude = store['longitude']
        mon = "Mon: " + store["mon_opening"] + " - " + store["mon_closing"]
        tue = " Tue: " + store["tue_opening"] + " - " + store["tue_closing"]
        wed = " Wed: " + store["wed_opening"] + " - " + store["wed_closing"]
        thu = " Thu: " + store["thu_opening"] + " - " + store["thu_closing"]
        fri = " Fri: " + store["fri_opening"] + " - " + store["fri_closing"]
        sat = " Sat: " + store["sat_opening"] + " - " + store["sat_closing"]
        sun = " Sun: " + store["sun_opening"] + " - " + store["sun_closing"]
        hours_of_operation = mon + tue + wed + thu + fri + sat + sun

        data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
