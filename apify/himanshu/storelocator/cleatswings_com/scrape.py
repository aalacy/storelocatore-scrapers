import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    base_url = "http://cleatswings.com"
    r = session.get("http://cleatswings.com/Cleats-Club-Seat-Grille-Locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("map",{'name':"Map"}).find_all("area"):
        location_request = session.get(base_url + "/" +  location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("h1",{'class':"title"}).text
        location_details = list(location_soup.find("div",{'class':"field-item even"}).stripped_strings)
        for i in range(len(location_details)):
            if len(location_details[i].split(",")) == 2:
                if len(location_details[i].split(",")[1].split(" ")[-1]) == 5:
                    address = location_details[i-1:i+1]
                    break
        for i in range(len(location_details)):
            if "Phone: " in location_details[i]:
                phone = location_details[i].split("Phone: ")[1]
                break
        for i in range(len(location_details)):
            if "Hours" in location_details[i]:
                hours = ""
                for k in range(i+1,len(location_details)):
                    if "$" in location_details[k]:
                        break
                    hours = hours + " " + location_details[k]
                break
        geo_location = location_soup.find("a",{'href':re.compile("/@")})["href"]
        store = []
        store.append("http://cleatswings.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[-1].split(" ")[-2])
        store.append(address[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("cleats")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
