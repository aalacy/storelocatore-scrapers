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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.adidas.com"
    r = session.get("https://placesws.adidas-group.com/API/search?brand=adidas&geoengine=google&method=get&category=store&latlng=39.683850419827884%2C-79.99448992936276%2C9000&page=1&pagesize=1000&fields=name%2Cstreet1%2Cstreet2%2Caddressline%2Cbuildingname%2Cpostal_code%2Ccity%2Cstate%2Cstore_o+wner%2Ccountry%2Cstoretype%2Clongitude_google%2Clatitude_google%2Cstore_owner%2Cstate%2Cperformance%2Cbrand_store%2Cfactory_outlet%2Coriginals%2Cneo_label%2Cy3%2Cslvr%2Cchildren%2Cwoman%2Cfootwear%2Cfootball%2Cbasketball%2Coutdoor%2Cporsche_design%2Cmiadidas%2Cmiteam%2Cstella_mccartney%2Ceyewear%2Cmicoach%2Copening_ceremony%2Coperational_status%2Cfrom_date%2Cto_date%2Cdont_show_country&format=json&storetype=ownretail",headers=headers)
    soup = BeautifulSoup(r.text,'html5lib')
    location_data = json.loads(str(soup).split("<body>")[1].split("</body>")[0].replace("<br>","").replace("\n",""))['wsResponse']["result"]
    for store_data in location_data:
        if store_data["country"] == "US" or store_data["country"] == "CA":
            store = []
            store.append("https://www.adidas.com")
            store.append(store_data["name"])
            address = ""
            if "street1" in store_data:
                address = address + " " + store_data["street1"]
            if "street2" in store_data:
                address = address + " " + store_data['street2']
            if "addressline" in store_data:
                address = address + " " + store_data["addressline"] 
            store.append(address.replace("&amp;","&"))
            store.append(store_data["city"])
            store.append(store_data["state"] if "state" in store_data else "<MISSING>")
            store.append(store_data["postal_code"])
            store.append(store_data["country"])
            store.append(store_data["id"])
            location_request = session.get("https://placesws.adidas-group.com/API/detail?brand=adidas&method=get&category=store&objectId=" + str(store_data["id"]) + "&format=json",headers=headers)
            soup1 = BeautifulSoup(location_request.text,'html5lib')
            location_data2 = json.loads(str(soup1).split("<body>")[1].split("</body>")[0].replace("<br>","").replace("\n",""))
            if location_data2["wsResponse"]["result"] == []:
                continue
            location_data = location_data2["wsResponse"]["result"][0]
            store.append(location_data["phone"].replace("001 (0)","").replace("+1","").strip() if "phone" in location_data else "<MISSING>")
            store.append(location_data['storetype'])
            store.append(location_data["latitude_google"])
            store.append(location_data["longitude_google"])
            hours = ""
            for key in location_data:
                if "openinghours" in key:
                    hours = hours + " " + key.split("_")[-1] + " " + location_data[key]
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<MISSING>")
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

