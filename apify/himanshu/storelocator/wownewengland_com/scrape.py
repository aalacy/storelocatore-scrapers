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
    base_url = "http://www.wownewengland.com"
    r = session.get("http://www.wownewengland.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("ul",{'class':"standar-dropdown standard drop_to_left sub-menu dropdown-menu"}).find_all("a"):
        if "/" not in location["href"]:
            continue
        location_url = location["href"]
        location_request = session.get(location_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location_soup.find("h2").stripped_strings)
        hours = " ".join(list(location_soup.find("h4").stripped_strings))
        name = location_soup.find("h1",{'class':"vc_custom_heading"}).text
        store = []
        store.append("http://www.wownewengland.com")
        store.append(name.capitalize())
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[-2])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(location_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
