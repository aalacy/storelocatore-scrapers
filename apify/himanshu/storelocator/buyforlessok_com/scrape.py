import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
    }
    addresses = []
    base_url = "http://www.buyforlessok.com"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = "https://buyforlessok.com/locations"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print("soup === "+ str(soup))
    for script in soup.find_all("div", {"class": "panel panel-default"}):
        hours_of_operation = script.find("div", {"class": "col-md-6 text-center"}).text.replace('Store Hours:','')
        phone = script.find("i", {"class": "fa fa-phone"}).nextSibling
        location_name = script.find("div", {"class": "panel-heading"}).text
        full_address = script.find("i", {"class": "fa fa-map-marker"}).parent.text
        # print("location_data === " + str(full_address))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
        state_list = re.findall(r' ([A-Z]{2}) ', full_address)
        if us_zip_list or state_list:
            zipp = us_zip_list[-1]
            state = state_list[-1]
            street_address = full_address.split("-")[0]
            city = full_address.split("-")[1].split(",")[0]
            geo_url = script.find("a")["href"]
            latitude = geo_url.split("/")[-1].split(",")[0]
            longitude = geo_url.split("/")[-1].split(",")[1]
            # print("latitude === " + latitude)
            # print("longitude === " + longitude)
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            if str(store[1]) + str(store[2]) not in addresses and "coming soon" not in location_name.lower():
                addresses.append(str(store[1]) + str(store[2]))
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
