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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://north40.com"
    r = session.get(base_url + "/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object  = []
    for location in soup.find_all("div",{"class":'hidden-xs col-sm-3'}):
        if location.find("a") == None:
            continue
        location_details = list(location.find("a").stripped_strings)
        location_request = session.get(base_url + location.find("a")['href'],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("div",{"class":"page-title"}).text
        location_address = list(location_soup.find("div",{"class":'nf-font-oswald-18r'}).stripped_strings)
        location_hours = list(location_soup.find_all("div",{"class":'nf-font-oswald-18r'})[3].stripped_strings)
        phone = location_details[-1]
        store = []
        store.append("https://north40.com")
        store.append(name.replace("\n"," "))
        store.append(location_address[0])
        store.append(location_address[-1].split(",")[0])
        if len(location_address[-1].split(",")) > 2:
            store.append(location_address[-1].split(",")[1])
        else:
            store.append(location_address[-1].split(",")[1].split(" ")[-2])
        store.append(location_address[-1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("north 40 outfitters")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("".join(location_hours))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
