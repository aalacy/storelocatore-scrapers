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
    base_url = "http://www.bagginsgourmet.com"
    r = session.get("http://www.bagginsgourmet.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"content-box-yellow"}):
        location_url = location.find("a",text="Location Details » ")["href"]
        location_request = session.get(base_url + location_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("h1",{'class':"entry-title"}).text
        location_details = list(location_soup.find("div",{'class':"one-half first"}).stripped_strings)[:-2]
        geo_location = location_soup.find("iframe")["src"]
        if "More" in location_details[-1]:
            location_details = location_details[:-1]
        if "Address" == location_details[0]:
            location_details = location_details[1:]
        for i in range(len(location_details)):
            if "Phone" in location_details[i]:
                phone = location_details[i+1]
                break
        for i in range(len(location_details)):
            if "Hours" in location_details[i]:
                hours = " ".join(location_details[i+1:])
                break
        store = []
        store.append("http://www.bagginsgourmet.com")
        store.append(name)
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-2])
        store.append(location_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("baggin's")
        store.append(geo_location.split("ll=")[1].split(",")[0] if "ll=" in geo_location else geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("ll=")[1].split(",")[1].split("&")[0] if "ll=" in geo_location else geo_location.split("!2d")[1].split("!")[0])
        store.append(hours.replace("–","-").replace("\xa0"," "))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
