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
    base_url = "https://tootntotum.com"
    r = session.get("https://tootntotum.com/locations",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    for city in soup.find_all("div",{"class":"tootntotum_city"}):
        address_name = city.find("h1").text
        for location in city.find_all("tr"):
            locationa_details = list(location.stripped_strings)
            if locationa_details[0].isdigit() == False:
                continue
            hours = " ".join(list(location.find_all("td")[3].stripped_strings))
            geo_location = location.find_all("a")[-1]["href"]
            store = []
            store.append("https://tootntotum.com")
            store.append(locationa_details[1])
            store.append(locationa_details[1])
            store.append(address_name.split(",")[0])
            store.append(address_name.split(",")[1] if len(address_name.split(",")) == 2 else "<MISSING>")
            store.append("<MISSING>")
            store.append("US")
            store.append(locationa_details[0])
            store.append(locationa_details[2])
            store.append("toot n totum")
            store.append(geo_location.split("/@")[1].split(",")[0] if len(geo_location.split("/@")) == 2 else "<INACCESSIBLE>")
            store.append(geo_location.split("/@")[1].split(",")[1] if len(geo_location.split("/@")) == 2 else "<INACCESSIBLE>")
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
