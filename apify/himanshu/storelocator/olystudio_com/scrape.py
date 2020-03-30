import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    base_url = "https://www.olystudio.com"
    data = "search%5Bstreet%5D=city+%26+state+or+zip+code&search%5Bradius%5D=100000&search%5Bmeasurement%5D=mi&search%5Blatitude%5D=&search%5Blongitude%5D=&search%5Btab%5D=0"
    r = session.post("https://www.olystudio.com/store-locator",headers=headers,data=data)
    soup = BeautifulSoup(r.text,"lxml")
    # getting the data from script tag
    for script in soup.find_all("script"):
        if "locationItems" in script.text:
            location_list = json.loads(script.text)["*"]["Magento_Ui/js/core/app"]["components"]["locationList"]["locationItems"]
            break
    
    for store_data in location_list:
        if store_data["country_id"] not in ("US", "CA"):
            continue
        store = []
        store.append("https://www.olystudio.com")
        store.append(store_data["title"])
        store.append(store_data["street"])
        store.append(store_data["city"])
        store.append(store_data["region"])
        store.append(store_data["zip"] if store_data["zip"] else "<MISSING>")
        store.append(store_data["country_id"])
        store.append(store_data["location_id"])
        store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
        store.append("oly")
        store.append(store_data["latitude"] if store_data["latitude"] != '0' else "<MISSING>")
        store.append(store_data["longitude"] if store_data["longitude"] != '0' else "<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
