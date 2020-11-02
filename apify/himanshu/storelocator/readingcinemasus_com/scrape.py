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
    base_url = "https://www.readingcinemasus.com"
    r = session.get("https://www.readingcinemasus.com/cinema-info",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("select",{'aria-label':"Select a Cinema"}).find_all("option")[1:]:
        location_request = session.get(location["value"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{'class':"address"}).find("ul").stripped_strings)
        store = []
        store.append("https://www.readingcinemasus.com")
        store.append(location_details[0])
        store.append(" ".join(location_details[1:-3]))
        store.append(location_details[-3].split(",")[0])
        store.append(location_details[-3].split(",")[1])
        store.append(location_details[-3].split(",")[2])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[-2])
        store.append("reading cinemasus")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
