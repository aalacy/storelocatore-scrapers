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

    base_link = "https://www.tirewarehouse.net/wp-json/monro/v1/stores/brand?brand=5"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    base = BeautifulSoup(req.text,"lxml")
    stores = json.loads(base.text.strip())["data"]

    data = []
    locator_domain = "tirewarehouse.net"

    for store in stores:
        location_name = "Tire Warehouse - " + store["City"]
        street_address = (store["Address"] + " " + store["Address2"]).strip()
        city = store['City']
        state = store["StateCode"]
        zip_code = store["ZipCode"]
        country_code = "US"
        store_number = store["Id"]
        location_type = "<MISSING>"
        phone = store['SalesPhone']
        hours_of_operation = ("Monday " + store["MondayOpenTime"] + "-" + store["MondayCloseTime"] + " Tuesday " + store["TuesdayOpenTime"] + "-" + store["TuesdayCloseTime"] + " Wednesday " + store["WednesdayOpenTime"] + "-" + \
        store["WednesdayCloseTime"] + " Thursday " + store["ThursdayOpenTime"] + "-" + store["ThursdayCloseTime"] + " Friday " + store["FridayOpenTime"] + "-" + store["FridayCloseTime"] + " Saturday " + \
        store["SaturdayOpenTime"] + "-" + store["SaturdayCloseTime"] + " Sunday " + store["SundayOpenTime"] + "-" + store["SundayCloseTime"]).strip().replace("00:00:00-00:00:00","Closed")
        latitude = store['Latitude']
        longitude = store['Longitude']
        link = "https://www.tirewarehouse.net/store-search/"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()