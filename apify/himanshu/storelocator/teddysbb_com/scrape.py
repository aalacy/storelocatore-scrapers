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
    base_url = "http://www.teddysbb.com"
    r = session.get("http://www.teddysbb.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":re.compile("mod_article")}):
        if location.find("a",{"href":re.compile("/@")}) == None:
            continue
        if location.parent.find("h3").text == "International":
            continue
        geo_location = location.find("a",{"href":re.compile("/@")})["href"]
        name = location.find("h6").text.replace("\xa0","")
        location_details = list(location.find("p").stripped_strings)[:-1]
        if len(location_details[1].split(",")) != 2:
            location_details[0] = " ".join(location_details[0:2])
            del location_details[1]
        store = []
        store.append("http://www.teddysbb.com")
        store.append(name)
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-2].split(".")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2].split("Phone:")[1])
        store.append("teddyy's")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append(" ".join(location_details[4:]).replace("–","-").replace("\xa0",""))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
