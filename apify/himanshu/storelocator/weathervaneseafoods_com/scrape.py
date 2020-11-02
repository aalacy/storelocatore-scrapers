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
    base_url = "https://weathervaneseafoods.com"
    r = session.get("https://weathervaneseafoods.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("li",{'class':"location col4 left"}):
        page_url = location.find("a")["href"]
        location_request = session.get(page_url,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location_soup.find("div",{'class':"address"}).stripped_strings)
        hours = " ".join(list(location_soup.find("div",{'class':"location-hours"}).stripped_strings)[:-1])
        phone = list(location_soup.find("div",{'class':"phone"}).stripped_strings)[0]
        name = location_soup.find("section",{'class':"location-heading"}).find("h1").text.strip()
        store = []
        store.append("https://weathervaneseafoods.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].replace(",",""))
        store.append(address[2])
        store.append(address[3])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("weathervane")
        geo_lcoation = location_soup.find_all("iframe")[-1]["src"]
        store.append(geo_lcoation.split("!3d")[1].split("!")[0])
        store.append(geo_lcoation.split("!2d")[1].split("!")[0])
        store.append(hours)
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
