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
    base_url = "http://premierecinemas.net"
    r = session.get("http://premierecinemas.net/contact",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    count = 0
    for location in soup.find_all("div",{'class':"twocol"}):
        location_details = list(location.stripped_strings)
        soup.find_all("iframe")[count]["src"]
        geo_request = session.get(soup.find_all("iframe")[count]["src"],headers=headers)
        count = count + 1
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
        store = []
        store.append("http://premierecinemas.net")
        store.append(location_details[0])
        store.append(geo_data.split(",")[0])
        store.append(geo_data.split(",")[1])
        store.append(geo_data.split(",")[-1].split(" ")[-2])
        store.append(geo_data.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(" ".join(location_details[2].replace("Phone: ","").split(" ")[0:2]))
        store.append("premiere cinemas")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
