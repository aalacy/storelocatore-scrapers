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
    base_url = "https://louiesgrillandbar.com"
    r = session.get("https://louiesgrillandbar.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':re.compile("card has-text-centered-mobile location-card has-background-accent")}):
        name = location.find("h2").text.strip()
        location_reqeust = session.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_reqeust.text,"lxml")
        store_hours = ""
        for hours in location_soup.find_all("p",{"class":'hours'}):
            store_hours = store_hours + " " + " ".join(list(hours.stripped_strings))
        address = list(location_soup.find("address").stripped_strings)[0].replace("           "," ")
        phone = location_soup.find("p",{'class':"phone"}).text.strip()
        store = []
        store.append("https://louiesgrillandbar.com")
        store.append(name)
        store.append(address.split(",")[0])
        store.append(address.split(",")[1])
        store.append(address.split(",")[-1].split(" ")[-2])
        store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("louie's")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(store_hours if store_hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
