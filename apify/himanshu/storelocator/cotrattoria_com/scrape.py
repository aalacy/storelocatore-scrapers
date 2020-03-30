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
    base_url = "https://cotrattoria.com"
    r = session.get("https://candorestaurants.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    count = 0
    for location in soup.find("div",{"class":"et_pb_row et_pb_row_1"}).find_all("div",{"class":re.compile("et_pb_column et_pb_column_1_3 et_pb_column_")}):
        if location.find("a") == None:
            continue
        location_request = session.get("https://candorestaurants.com" + location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        details_request = session.get(location_soup.find_all("a",text="Contact Us")[count]["href"],headers=headers)
        details_soup = BeautifulSoup(details_request.text,"lxml")
        count = count + 1
        location_details = list(details_soup.find("div",{'class':"et_pb_text_inner"}).stripped_strings)
        store = []
        store.append("https://cotrattoria.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[-1].split(" ")[-2])
        store.append(location_details[2].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[4] if "(" in location_details[4] else "(" + location_details[4])
        store.append("cando restaurants")
        geo_location = details_soup.find("iframe")["src"]
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
