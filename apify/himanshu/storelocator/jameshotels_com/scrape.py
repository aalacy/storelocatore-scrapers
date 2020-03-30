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
    base_url = "https://www.jameshotels.com"
    r = session.get("https://www.jameshotels.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("li",{'id':"menu-item-12656"}).find_all("a"):
        name = location.text.strip()
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("span",text=re.compile("COMING SOON")):
            continue
        address = list(location_soup.find_all("address")[-1].find("p").stripped_strings)
        if len(address) == 4:
            address = address[1:-1]
        if len(address) == 3:
            address[1] = " ".join(address[1:])
            del address[-1]
        phone = location_soup.find_all("address")[-1].find("a",{'href':re.compile("tel:")}).text
        if location_soup.find("a",{"href":re.compile("/@")}) == None:
            geo_location = ""
        else:
            geo_location = location_soup.find("a",{"href":re.compile("/@")})["href"]
        store = []
        store.append("https://www.jameshotels.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[-2])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("the james hotels")
        store.append(geo_location.split("/@")[1].split(",")[0] if geo_location != "" else "<MISSING>")
        store.append(geo_location.split("/@")[1].split(",")[1] if geo_location != "" else "<MISSING>")
        store.append("<MISSING>")
        for i in range(len(store)):
            store[i] = store[i].replace("–","-")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
