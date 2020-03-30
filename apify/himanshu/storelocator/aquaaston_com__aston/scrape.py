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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.aquaaston.com"
    r = session.get("https://www.aquaaston.com/destinations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("a",{"title":""}):
        if "/hotels" not in location["href"] or location["href"] == "/hotels" or "?" in location["href"]:
            continue
        location_request = session.get(base_url + location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("script",{'type':"application/ld+json"}) == None:
            store = []
            store.append("https://www.aquaaston.com")
            store.append(location.text)
            store.append(location_soup.find("span",{"itemprop":"streetAddress"}).text)
            store.append(location_soup.find("span",{"itemprop":"addressLocality"}).text)
            store.append(location_soup.find("span",{"itemprop":"addressRegion"}).text)
            store.append(location_soup.find("span",{"itemprop":"postalCode"}).text)
            store.append("US")
            store.append("<MISSING>")
            store.append(location_soup.find("span",{"itemprop":"telephone"}).text)
            store.append("<MISSING>")
            for script in location_soup.find_all("script"):
                if "&lat=" in script.text:
                    lat = script.text.split("&lat=")[1].split("&")[0]
                    lng = script.text.split("&lat=")[1].split("&lon=")[1].split("'")[0]
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(base_url + location["href"])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
        else:
            store_data = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text, strict=False)
            if store_data["address"]["addressLocality"] == "":
                continue
            store = []
            store.append("https://www.aquaaston.com")
            store.append(location.text)
            store.append(store_data["address"]["streetAddress"])
            store.append(store_data["address"]["addressLocality"] if store_data["address"]["addressLocality"] else "<MISSING>")
            store.append(store_data["address"]["addressRegion"] if store_data["address"]["addressRegion"] else "<MISSING>")
            store.append(store_data["address"]["postalCode"] if store_data["address"]["postalCode"] else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["telephone"])
            store.append("<MISSING>")
            store.append(store_data["hasMap"].split("q=")[1].split(",")[0])
            store.append(store_data["hasMap"].split("q=")[1].split(",")[1])
            store.append("<MISSING>")
            store.append(base_url + location["href"])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
