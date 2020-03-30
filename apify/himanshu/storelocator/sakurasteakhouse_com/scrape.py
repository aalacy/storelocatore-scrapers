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
    base_url = "https://sakurasteakhouse.com"
    r = session.get("https://sakurasteakhouse.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"fusion-layout-column"}):
        if location.find("h3") == None:
            continue
        if location.find("li",{'class':"fusion-li-item"}) == None:
            continue
        name = location.find("h3").text
        city = location.find("h3").text.replace(" Sakura","")
        address = location.find("li",{'class':"fusion-li-item"}).text.strip().replace(city,"")
        phone = location.find_all("li",{'class':"fusion-li-item"})[1].text.strip()
        store = []
        store.append("https://sakurasteakhouse.com")
        store.append(name)
        store.append(" ".join(address.split(",")[0:-1]))
        store.append(city)
        store.append(address.split(",")[-1].split(" ")[-2])
        store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("sakura")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
