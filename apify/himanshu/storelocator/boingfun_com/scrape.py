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
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    base_url = "https://www.boingfun.com/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    location_reqeust = session.get("https://orlando.boingfun.com/",headers=header)
    location_soup = BeautifulSoup(location_reqeust.text,"lxml")
    location_details = list(location_soup.find("div",{"class":"textwidget custom-html-widget"}).stripped_strings)
    store = []
    store.append("https://www.boingfun.com/")
    store.append(location_details[0])
    store.append(location_details[1])
    store.append(location_details[2].split(",")[0])
    store.append(location_details[2].split(",")[-1].split(" ")[-2])
    store.append(location_details[2].split(",")[-1].split(" ")[-1])
    store.append("US")
    store.append("<MISSING>")
    store.append(location_details[4])
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append(" ".join(location_details[6:]).split("information. Hours")[1])
    store.append("https://orlando.boingfun.com/")
    yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
