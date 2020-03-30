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
    base_url = "https://www.zyn22.com"
    r = session.get("https://www.zyn22.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"overlay-reveal"}):
        location_details = list(location.stripped_strings)
        location_url = location.find_all("a")[-1]["href"]
        location_request = session.get(location_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        geo_lcoation = location_soup.find("section",{"class":"map-embed"}).find("iframe")["src"]
        store = []
        store.append("https://www.zyn22.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(geo_lcoation.split("!2s")[1].split("!")[0].split("%2C")[1].replace("+"," "))
        store.append(geo_lcoation.split("!2s")[1].split("!")[0].split("%2C")[2].split("+")[1])
        store.append(geo_lcoation.split("!2s")[1].split("!")[0].split("%2C")[2].split("+")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2])
        store.append("zyn 22")
        store.append(geo_lcoation.split("!3d")[1].split("!")[0])
        store.append(geo_lcoation.split("!2d")[1].split("!")[0])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
