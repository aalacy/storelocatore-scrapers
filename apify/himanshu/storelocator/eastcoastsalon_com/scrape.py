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
    base_url = "https://www.eastcoastsalon.com"
    r = session.get("https://www.eastcoastsalon.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    
    return_main_object = []
    for tr in soup.find("table").find_all("tr"):
        addr = list(tr.find("td").stripped_strings)
        if "DuBois, PA" == addr[0] or "McMurray, PA" == addr[0] or "Parsippany, NJ" == addr[0]:
            location_name = "<MISSING>"
            street_address = addr[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[-1].split()[0]
            zipp = addr[2].split(",")[-1].split(" ")[-1]
        else:
            location_name = addr[1]
            street_address = addr[2]
            city = addr[3].split(",")[0]
            state = addr[3].split(",")[-1].split()[0]
            zipp = addr[3].split(",")[-1].split(" ")[-1]

        phone = list(tr.find_all("td")[-1].stripped_strings)[1]
        
        store = []
        store.append("https://www.eastcoastsalon.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("https://www.eastcoastsalon.com/locations")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
