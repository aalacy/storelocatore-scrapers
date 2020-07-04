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
    base_url = "https://bergmanluggage.com"
    r = session.get("https://bergmanluggage.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for state in soup.find("li",{"class":re.compile("store-locations")}).find_all("ul",{"class":re.compile("navmenu-depth-3")})[1:]:
        for page in state.find_all("a"):
            page_request = session.get(base_url + page["href"],headers=headers)
            page_soup = BeautifulSoup(page_request.text,"lxml")
            data = json.loads(page_soup.find("div",{"develic-map":re.compile('{')})["develic-map"])["items"]
            # print(data)
            for i in range(len(data)):
                store_data = data[i]
                if "STORE IS CLOSED" in store_data['t']:
                    continue
                address = list(BeautifulSoup(store_data["b"],"lxml").stripped_strings)
                if "This Location Has Closed" in address:
                    continue
                store = []
                store.append("https://bergmanluggage.com")
                store.append(store_data["t"])
                store.append(" ".join(address[0].split(",")[0:-3]))
                store.append(address[0].split(",")[-3])
                store.append(address[0].split(",")[-2].split(" ")[-2])
                store.append(address[0].split(",")[-2].split(" ")[-1])
                store.append("US")
                store.append("<MISSING>")
                store.append(address[1] if len(address) == 2 else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["lt"])
                store.append(store_data["lg"])
                store.append("<MISSING>")
                store.append(base_url + page["href"])
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
