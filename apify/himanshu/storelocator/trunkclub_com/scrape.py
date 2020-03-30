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
    base_url = "https://www.trunkclub.com"
    r = session.get("https://www.trunkclub.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("ul",{"class":'margin-T--md'})[2].find_all("li"):
        link = location.find("a")["href"]
        location_request = session.get(base_url + link)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        store_data = json.loads(location_soup.find("script",{"type":"application/ld+json"}).text)
        hours = location_soup.find_all("div",{"class":"u-size-Full margin-B--md"})
        store_hours = ""
        for k in range(len(hours)):
            store_hours = store_hours + hours[k].text.strip() + " "
        store = []
        store.append("https://www.trunkclub.com")
        store.append(store_data["name"])
        store.append(store_data["address"]["streetAddress"])
        store.append(store_data["address"]["addressLocality"])
        store.append(store_data["address"]["addressRegion"])
        store.append(store_data["address"]["postalCode"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["telephone"])
        store.append("trunk club")
        store.append(store_data["geo"]["latitude"])
        store.append(store_data["geo"]["longitude"])
        store.append(store_hours.replace("\n"," "))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
