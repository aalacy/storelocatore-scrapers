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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.lawlersbarbecue.com"
    json_data = session.get("https://gusto-dataaccessapi.azurewebsites.net/api/v2/2099/Location").json()
    phone_dict = {}
    for data in json_data:
        phone_dict[data['Phone']] = data['LocationID']
    # print(phone_dict)
    r = session.get("https://www.lawlersbarbecue.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    for script in soup.find_all("script",{"type":'application/ld+json'}):
        if '"location":' in script.text:
            location_list = json.loads(script.text)["location"]
            
            for store_data in location_list:
                store = []
                store.append("https://www.lawlersbarbecue.com")
                store.append(store_data["name"])
                if " - " in store_data["name"]:
                    store_data["name"] = store_data["name"].split(" - ")[1]
                store.append(store_data["address"]["streetAddress"])
                store.append(store_data["address"]["addressLocality"])
                store.append(store_data["address"]["addressRegion"])
                store.append(store_data["address"]["postalCode"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["telephone"])
                phone_data = store_data["telephone"].replace("+1(","").replace(")","").replace("-","").replace(" ","")
                try:
                    page_url = ("https://order-online.azurewebsites.net/2099/"+str(phone_dict[phone_data])+"/")
                except:
                    page_url = "<MISSING>"
                store.append("law lers barbecue")
                coords = session.get(store_data["image"]).url
                
                store.append(coords.split("/%40")[1].split(",")[0])
                # print(coords.split("/%40")[1].split(",")[1])
                store.append(coords.split("/%40")[1].split(",")[1])
                store.append(" ".join(store_data["openingHours"]))
                store.append(page_url)
                if "37091" in store_data["address"]["postalCode"]:
                    continue
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
