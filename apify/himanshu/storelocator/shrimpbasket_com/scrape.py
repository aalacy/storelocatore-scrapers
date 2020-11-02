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
    base_url = "https://shrimpbasket.com"
    r = session.get("https://shrimpbasket.com/location",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "address_details_array.push(" in script.text:
            for location in script.text.split("address_details_array.push(")[1:]:
                location_details = json.loads(location.split("]);")[0] + "]")
                location_soup = BeautifulSoup(location.split("var property_item = `")[1].split("`")[0],"lxml")
                address = list(location_soup.find("span").stripped_strings)
                phone = location_soup.find("a").text
                store = []
                store.append("https://shrimpbasket.com")
                store.append(location_details[0])
                store.append(address[0])
                store.append(address[1].split(",")[0])
                store.append(location_details[-1])
                store.append("<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("shrimp basket")
                store.append(location_details[-3])
                store.append(location_details[-2])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
