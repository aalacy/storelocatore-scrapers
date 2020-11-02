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
    base_url = "http://www.fademasters.com"
    r = session.get("http://www.fademasters.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    hours = " ".join(list(soup.find("div",{"id":"text-7"}).stripped_strings))
    for location in soup.find_all("div",{'class':"et_pb_promo_description"}):
        location_details = list(location.stripped_strings)
        geo_location = location.find("a",{"href":re.compile("/@")})["href"]
        store = []
        store.append("http://www.fademasters.com")
        store.append(location_details[0])
        store.append(location_details[2])
        store.append(" ".join(location_details[-1].split(" ")[0:-2]))
        store.append(location_details[-1].split(" ")[-2])
        store.append(location_details[-1].split(" ")[-1])
        store.append("US")
        store.append(location_details[0].split(" ")[1])
        store.append(location_details[1])
        store.append("fade  masters")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
