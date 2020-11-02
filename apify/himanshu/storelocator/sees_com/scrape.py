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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.sees.com"
    r = session.get("https://maps.sees.com/api/getAsyncLocations?template=search&level=search&radius=500000&search=11756",headers=headers)
    data = r.json()["markers"]
    return_main_object = []
    for store_data in data:
        store_soup = BeautifulSoup(store_data["info"],"lxml")
        page_url = json.loads(store_soup.find("div").text)["url"]
        location_request = session.get(page_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        for script in location_soup.find_all("script"):
            if "dataLayer.push" in script.text:
                country = script.text.split("country")[1].split(",")[0].replace(":","").replace("'","").replace(" ",'')
        if country not in ["CA","US"]:
            continue
        location_details = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text)[0]
        store = []
        store.append("https://www.sees.com")
        store.append(location_details["name"])
        store.append(location_details["address"]["streetAddress"])
        store.append(location_details["address"]["addressLocality"])
        store.append(location_details["address"]["addressRegion"])
        store.append(location_details["address"]["postalCode"])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details["address"]["telephone"] if location_details["address"]["telephone"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(location_details["geo"]["latitude"])
        store.append(location_details["geo"]["longitude"])
        store.append(location_details["openingHours"])
        store.append(page_url)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
