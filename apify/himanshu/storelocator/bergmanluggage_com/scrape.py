import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline='') as output_file:
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
    base_url = "https://bergmanluggage.com"
    r = session.get("https://bergmanluggage.com/pages/all-store-locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    json_data = json.loads(soup.find("div",{"develic-map":re.compile('{')})["develic-map"])["items"]
    
    
    for data in json_data:
        
        if "STORE IS CLOSED" in data['t']:
            continue
        address = list(BeautifulSoup(data["b"],"lxml").stripped_strings)
        if "This Location Has Closed" in address:
            continue
        
        store = []
        store.append(base_url)
        store.append(data["t"])
        if "USA" in address[0]:
            store.append(" ".join(address[0].split(",")[0:-3]))
            store.append(address[0].split(",")[-3].strip())
            store.append(address[0].split(",")[-2].split(" ")[-2])
            store.append(address[0].split(",")[-2].split(" ")[-1])
        else:
            store.append(" ".join(address[0].split(",")[0:-2]))
            store.append(address[0].split(",")[-2].strip())
            store.append(address[0].split(",")[-1].split(" ")[-2])
            store.append(address[0].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[1] if len(address) == 2 else "<MISSING>")
        store.append("<MISSING>")
        store.append(data["lt"])
        store.append(data["lg"])
        store.append("<MISSING>")
        store.append("https://bergmanluggage.com/pages/all-store-locations")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
