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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.lapetite.com"
    data = 'location=11756&range=10000'
    r = session.post("https://www.lapetite.com/locations/",headers=headers,data=data)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"locationCard"}):
        name = location.find("a",{'class':"schoolNameLink"}).text
        address = location.find("span",{'class':"street"}).text
        address2 = location.find("span",{'class':"cityState"}).text
        store_id = location["data-school-id"]
        if location.find("span",{'class':"tel"}) != None:
            phone = location.find("span",{'class':"tel"}).text
        elif location.find("p",{'class':"phone"}) != None:
            phone = list(location.find("p",{'class':"phone"}).stripped_strings)[-1]
        else:
            phone = "<MISSING>"
        hours = " ".join(list(location.find("p",{'class':"hours"}).stripped_strings))
        store = []
        store.append("https://www.lapetite.com")
        store.append(name)
        store.append(address)
        store.append(address2.split(",")[0])
        store.append(address2.split(",")[1].split(" ")[1])
        store.append(address2.split(",")[1].split(" ")[-1])
        store.append("US")
        store.append(store_id)
        store.append(phone if phone != "" else "<MISSING>")
        store.append("lapetite")
        store.append(location.find("span",{"class":"addr"})["data-latitude"])
        store.append(location.find("span",{"class":"addr"})["data-longitude"])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
