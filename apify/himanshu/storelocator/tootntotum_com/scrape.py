import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://tootntotum.com"
    r = session.get("https://stockist.co/api/v1/u4882/locations/all.js?callback=_stockistAllStoresCallback",headers=headers)
    address = []
    soup = BeautifulSoup(r.text,"lxml")
    data = (soup.text.replace(');',"").split("_stockistAllStoresCallback(")[1])
    json_data = json.loads(data)
    for i in json_data:
        location_type = str(i['name']).split(" #")[0]
        store_number = str(i['name']).split(" #")[1]
        store = []
        store.append("https://tootntotum.com")
        store.append(i['name'] if i['name'] else "<MISSING>")
        store.append(i['address_line_1'] if i['address_line_1'] else "<MISSING>")
        store.append(i['city'] if i['city'] else "<MISSING>")
        store.append(i["state"] if i['state'] else "<MISSING>")
        store.append(i["postal_code"] if i['postal_code'] else "<MISSING>")
        store.append(i["country"] if i['country'] else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(i['phone'] if i['phone'] else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(i['latitude'] if i['latitude'] else "<MISSING>")
        store.append(i['longitude'] if i['longitude'] else "<MISSING>")
        store.append(str(i['custom_fields']).replace("[{'id': 873, 'name': 'Hours', 'value': '","").replace('}]',"").replace("}","").replace("{","").replace("\\n","").replace("PM","PM ").replace("AMSun","AM Sun").replace(" 'id': 1052, 'name': ","").replace("', 'value': "," - ").replace("AMSat","AM Sat").replace('Wash',"Wash ").replace('Car Care',"Car Care ").replace("'",""))
        store.append("https://tootntotum.com/locations")
        # if store[2] in address :
        #     continue
        # address.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
