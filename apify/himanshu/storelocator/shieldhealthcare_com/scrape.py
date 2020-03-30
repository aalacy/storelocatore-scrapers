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
    base_url = "https://shieldhealthcare.com"
    r = session.get("https://shieldhealthcare.com/company/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class": "cityWrapper"}):
        name = " ".join(list(location.find("div",{'class':'cityHeader'}).stripped_strings))
        phone = list(location.find("div",{'class':'phoneWrapper'}).stripped_strings)[1]
        if location.find("div",{'class':'addressWrapper'}) == None:
            continue
        location_details = list(location.find("div",{'class':'addressWrapper'}).stripped_strings)
        if location_details == []:
            continue
        store = []
        store.append("https://shieldhealthcare.com")
        store.append(name)
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-2])
        store.append(location_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("shield health care")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    store = []
    location_details = list(soup.find("div",{"class":"addressWrapper"}).stripped_strings)
    phone = list(soup.find("div",{'class':'phoneWrapper'}).stripped_strings)[2]
    store.append("https://shieldhealthcare.com")
    store.append(location_details[0])
    store.append(location_details[1])
    store.append(location_details[2].split(",")[0])
    store.append(location_details[2].split(",")[1].split(" ")[-2])
    store.append(location_details[2].split(",")[1].split(" ")[-1])
    store.append("US")
    store.append("<MISSING>")
    store.append(phone)
    store.append("shield health care")
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append("<MISSING>")
    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
