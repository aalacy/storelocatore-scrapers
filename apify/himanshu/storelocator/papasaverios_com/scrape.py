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
    base_url = "https://papasaverios.com"
    r = session.get("https://papasaverios.com/all-locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{'class':"accordion-body"}).find_all("li"):
        location_reqeust = session.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_reqeust.text,"lxml")
        location_details = list(location_soup.find('div',{'class':"section-location"}).stripped_strings)[:-2]
        address = location_details[3].replace("\t","")[:-1]
        if address[-1] == " ":
            address = address[:-1]
        geo_location = location_soup.find("a",text="map it")["href"]
        store = []
        store.append("https://papasaverios.com")
        store.append(location_details[0])
        if "COMING SOON" in store[-1]:
            continue
        if len(address.split(",")) == 4:
            store.append(" ".join(address.split(",")[:-2]))
            store.append(address.split(",")[2])
        elif len(address.split(",")) == 3:
            store.append(address.split(",")[0])
            store.append(address.split(",")[1])
        else:
            store.append(" ".join(address.split(",")[0].split(".")[0:-1]))
            store.append(address.split(",")[0].split(".")[-1])
        store.append(address.split(",")[-1].split(" ")[-2])
        store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2].split("Phone:")[1] if "Coming Soon!" not in location_details[2].split("Phone:")[1] else "<MISSING>")
        store.append("<MISSING>")
        store.append(geo_location.split("q=loc:")[1].split(",")[0])
        store.append(geo_location.split("q=loc:")[1].split(",")[1])
        store.append(" ".join(location_details[6:]) if " ".join(location_details[6:]) != "" else "<MISSING>")
        store.append("https://papasaverios.com/all-locations")
        store = [x.replace("–","-") for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
