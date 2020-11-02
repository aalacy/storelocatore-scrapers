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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    base_url = "https://boathouserestaurants.ca"
    r = session.get("https://boathouserestaurants.ca/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find("div",{"id":"menu_content"}).prettify().split("<hr"):
        location_soup = BeautifulSoup(location,"lxml")
        location_details = list(location_soup.find("h3").parent.parent.stripped_strings)
        store = []
        store.append("https://boathouserestaurants.ca")
        store.append(location_details[0])
        store.append(location_details[-3])
        store.append(location_details[-2].split(",")[0])
        store.append(location_details[-2].split(",")[1])
        store.append(location_details[-1])
        store.append("CA")
        store.append("<MISSING>")
        store.append(location_details[-4].replace("KITS",""))
        store.append("<MISSING>")
        geo_location = location_soup.find("a",{'target':"_blank"})["href"]
        store.append(geo_location.split("sll=")[1].split(",")[0])
        store.append(geo_location.split("sll=")[1].split(",")[1].split("&")[0])
        hours = " ".join(list(location_soup.find_all("div",{"class":"row"})[-1].stripped_strings))
        store.append(hours if hours else "<MISSING>")
        store.append("https://boathouserestaurants.ca/locations/")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()