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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://codysoriginalroadhouse.com"
    r = session.get("https://codysoriginalroadhouse.com/locations.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{"class":"clearfix grpelem"}).find_all("a",{'class':'nonblock nontext grpelem'}):
        if "/" in location["href"]:
            continue
        location_request = session.get(base_url + "/" +  location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("div",{'class':"clearfix colelem","id":re.compile("-")}) == None:
            continue
        location_details = list(location_soup.find("div",{'class':"clearfix colelem","id":re.compile("-")}).stripped_strings)
        if "Hours of Operation:" not in location_details:
            continue
        for i in range(len(location_details)):
            if "Hours" in location_details[i]:
                hours = " ".join(location_details[i+1:])
        if len(location_details[0].split(",")) == 3:
            location_details.insert(1,"")
            location_details[1] = ",".join(location_details[0].split(",")[1:])[1:]
            location_details[0] = location_details[0].split(",")[0]
        name = location["href"].replace(".html","")
        geo_location = location_soup.find("iframe")["src"]
        store = []
        store.append("https://codysoriginalroadhouse.com")
        store.append(name)
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[-1].split(" ")[-2].replace(".","").replace("\xa0"," "))
        store.append(location_details[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2].replace("Phone:","").replace("\xa0"," "))
        store.append("cody's original roadhouse")
        if "&sll=" in geo_location:
            store.append(geo_location.split("&sll=")[1].split(",")[0])
            store.append(geo_location.split("&sll=")[1].split(",")[1].split("&")[0])
        else:
            store.append(geo_location.split("!3d")[1].split("!")[0])
            store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(hours.replace("\xa0"," ").replace("â\x80\x93"," "))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
