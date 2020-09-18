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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.pollyspies.com"
    r = session.get("https://www.pollyspies.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"row location"}):
        link = location.find("a")["href"]
        location_request = session.get(link,headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location_soup.find("div",{"class":"address"}).find('a').stripped_strings)
        hours = " ".join(list(location_soup.find("div",{"class":"hours"}).stripped_strings))
        if hours == "Permanently Closed":
            continue
        phone = location_soup.find("div",{'class':"telephone"}).text.strip()
        for script in location_soup.find_all("script"):
            if "var single_location_lat = " in script.text:
                lat = script.text.split("var single_location_lat = ")[1].split(";")[0]
                lng = script.text.split("var single_location_lng = ")[1].split(";")[0]
        name = location_soup.find("h1").text
        store = []
        store.append("https://www.pollyspies.com")
        store.append(link)
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1])
        store.append(address[1].split(",")[2])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
