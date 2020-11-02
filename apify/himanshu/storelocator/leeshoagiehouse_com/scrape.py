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
    base_url = "http://leeshoagiehouse.com"
    r = session.get("http://leeshoagiehouse.com/order/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"item"}):
        name = location.find("div",{"class":"title"}).text.strip()
        address = location.find("p",{'class':'address-wrap'}).text.strip()
        state_split = re.findall("([A-Z]{2})",address)
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        store_zip_split = re.findall(r"[0-9]{5}(?:-[0-9]{4})?",address)
        if store_zip_split:
            store_zip = store_zip_split[-1]
        else:
            store_zip = "<MISSING>"
        city = name.split(",")[0]
        street_address = address.replace(store_zip,"").replace(state,"").replace(city,"").replace("\n"," ")
        if " ," in street_address:
            pass
        else:
            city = street_address.split(",")[0].split(" ")[-1]
            street_address = street_address.replace(city,"")
        if location.find("p",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")):
            phone = location.find("p",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")).text
        else:
            phone = "<MISSING>"
        store_id = location["class"][1].split("-")[1]
        hours = " ".join(list(location.find("div",{'class':'content'}).find_all("p")[-1].stripped_strings))
        store = []
        store.append("http://leeshoagiehouse.com")
        store.append(name)
        store.append(street_address.replace(", ",""))
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append(store_id)
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append("http://leeshoagiehouse.com/order")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
