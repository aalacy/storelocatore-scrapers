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
    base_url = "https://thevarsity.com"
    r = session.get("https://thevarsity.com/locations",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("div",{"class":"store-listing"}):
        name = location.find("div",{"class":"store-listing-name"}).find("a").text.strip()
        address = list(location.find("div",{"class":"store-listing-address"}).stripped_strings)
        phone = location.find("div",{"class":"store-listing-phone"}).text
        location_request = session.get(base_url + location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_hours = list(location_soup.find("div",{"class":'col-xs-12 col-sm-8 col-md-6'}).stripped_strings)
        hours = ""
        for k in range(len(location_hours)):
            if "Hours of Operation" in location_hours[k]:
                for j in range(k+1,len(location_hours)):
                    if "Find Us" in location_hours[j]:
                        break
                    hours = hours + location_hours[j] + " "
                break
        store = []
        store.append("https://thevarsity.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[1])
        store.append(address[1].split(",")[1].split(" ")[2])
        store.append("US")
        store.append(location.find("a")["href"].split("/")[3])
        store.append(phone)
        store.append("varsity")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
