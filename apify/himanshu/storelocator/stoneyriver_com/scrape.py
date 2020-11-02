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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://stoneyriver.com"
    r = session.get("https://stoneyriver.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"flexWrapper"}):
        address = list(location.find("address").stripped_strings)
        if len(address) == 4:
            address[0] = " ".join(address[0:2])
            del address[1]
        address[1] = address[1].replace("\t"," ")
        address[0] = address[0].replace("\t"," ")
        if "       " in address[1]:
            address[0] = address[0] + address[1].split("       ")[0]
            address[1] = address[1].split("       ")[1]
        phone = address[-1]
        hours = " ".join(list(location.find("div",{'class':'details hours'}).stripped_strings)[1:]).strip()
        store = []
        store.append("https://stoneyriver.com")
        store.append(location.find("h4").text)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(" ".join(address[1].split(",")[1].split(" ")[1:-1]))
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store_id = json.loads(location.find("a")["data-resy"])["venueId"]
        store.append(store_id)
        store.append(phone)
        store.append("stoney river")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours.replace("–","-") if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
