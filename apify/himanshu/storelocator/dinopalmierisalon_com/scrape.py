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
    base_url = "https://www.dinopalmierisalon.com/"
    r = session.get("https://www.dinopalmierisalon.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("ul",{'class':"sm-nav-list sm-nav-align-center sm-col-align-center"}).find_all("a")[:-2]:
        if "locations/" not in location["href"]:
            continue
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text.replace("</br>","<br>"),"lxml")
        address = list(location_soup.find("h5",{'class':"uabb-infobox-title"}).stripped_strings)
        phone = list(location_soup.find_all("h5",{'class':"uabb-infobox-title"})[1].stripped_strings)[0]
        hours = " ".join(list(location_soup.find_all("h5",{'class':"uabb-infobox-title"})[2].stripped_strings))
        store = []
        store.append("https://www.dinopalmierisalon.com")
        store.append(location_soup.find("h1").text)
        store.append(" ".join(address[0:-1]))
        store.append(address[-1].split(",")[0])
        store.append(address[-1].split(",")[-1].split(" ")[-2])
        store.append(address[-1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("dino palmieri salon & spa")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours.replace('–',"-"))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
