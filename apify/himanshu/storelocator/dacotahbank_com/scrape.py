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
    base_url = "https://www.dacotahbank.com"
    r = session.get("https://www.dacotahbank.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for locations in soup.find_all("div",{'class':"large-6 columns"}):
        geo_location = locations.find("a",text="Get Directions")["href"]
        location_details = list(locations.stripped_strings)[:-2]
        store = []
        store.append("https://www.dacotahbank.com")
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1])
        store.append(location_details[1].split(",")[2].split(" ")[-2])
        store.append(location_details[1].split(",")[2].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2].split("Phone ")[1].split("|")[0])
        store.append("dacotah bank")
        lat = geo_location.split("/@")[1].split(",")[0]
        lng = geo_location.split("/@")[1].split(",")[1]
        store.append(lat)
        store.append(lng)
        location_request = session.get(base_url + locations.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours = ""
        for store_hours in location_soup.find_all("table",{"class":"hours-table"}):
            hours = hours + " " + " ".join(list(store_hours.stripped_strings))
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
 




