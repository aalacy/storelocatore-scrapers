import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
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
    base_url = "https://www.bankoftampa.com"
    r = session.get("https://www.bankoftampa.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_location = {}
    for locations in soup.find("div",{'class':"map"}).find_all("div"):
        for location in json.loads(locations["data-options"])["locations"]:
            geo_location[location["address"]] = location["coordinates"]
    for location in soup.find("div",{'class':"col-sm-6"}).find_all("a"):
        location_request = session.get(base_url + location['href'],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("div",{"class":"main-content container"}).find("h1").text
        if location_soup.find("div",{"class":"col-sm-6 address"}) == None:
            continue
        address = list(location_soup.find("div",{"class":"col-sm-6 address"}).stripped_strings)
        if len(address[2].split(",")) == 1:
            address[1] = " ".join(address[1:3])
            del address[2]
        if location_soup.find("h2",text="Hours") == None:
            hours = "<MISSING>"
        else:
            hours = " ".join(list(location_soup.find("h2",text="Hours").parent.stripped_strings))
        store = []
        store.append("https://www.bankoftampa.com")
        store.append(name)
        store.append(address[1])
        store.append(address[2].split(",")[0])
        if len(address[2].split(",")) == 3:
            store.append(address[2].split(",")[1])
            store.append(address[2].split(",")[2])
        else:
            store.append(address[2].split(",")[1].split(" ")[-2])
            store.append(address[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-2])
        store.append("the bank of tampa")
        store.append(geo_location[base_url + location['href']][0] if base_url + location['href'] in geo_location else "<MISSING>")
        store.append(geo_location[base_url + location['href']][1] if base_url + location['href'] in geo_location else "<MISSING>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
