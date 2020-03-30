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
    base_url = "https://firstknox.com"
    r = session.get("https://firstknox.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    page_number = int(soup.find_all("a",{'class':"page-numbers"})[-2]["href"].split("/")[-2])
    for i in range(1,page_number + 2):
        page_request = session.get("https://firstknox.com/locations/page/"+ str(i) + "/",headers=headers)
        page_soup = BeautifulSoup(page_request.text,"lxml")
        location_object = []
        for script in page_soup.find_all("script"):
            if "var markers = " in script.text:
                location_list = json.loads(script.text.split("var markers = ")[1].split("}]")[0] + "}]")
                for i in range(len(location_list)):
                    location_object.append([location_list[i]["lat"],location_list[i]["lng"],location_list[i]["phone"]])
        for location in page_soup.find_all('div',{'class':"location-list-result"}):
            name = location.find("span",{'class':'sub-head fw-light'}).find("a").text
            address = list(location.find("span",{'class':"branch-address fw-light"}).stripped_strings)
            hours = " ".join(list(location.find("div",{'class':'branch-hours'}).stripped_strings))
            store = []
            store.append("https://firstknox.com")
            store.append(name)
            store.append(address[0])
            store.append(address[1].split(",")[0])
            store.append(address[1].split(",")[-1].split(" ")[-2])
            store.append(address[1].split(",")[-1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(location_object[0][-1])
            store.append("first knox national bank")
            store.append(location_object[0][0])
            store.append(location_object[0][1])
            del location_object[0]
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
