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
    base_url = "https://luckybaldwins.pub"
    r = session.get("https://luckybaldwins.pub",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    
    for location in soup.find_all("a",class_="fl-callout-title-link fl-callout-title-text"):
        
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        
        geo_request = session.get(location_soup.find("iframe")["data-src"],headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                phone = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][7]
        store = []
        store.append("https://luckybaldwins.pub")
        store.append(geo_data.split(",")[0])
        store.append(geo_data.split(",")[1].strip())
        store.append(geo_data.split(",")[2].strip())
        store.append(geo_data.split(",")[3].split(" ")[1])
        store.append(geo_data.split(",")[3].split(" ")[2])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("lucky baldwins")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(location['href'])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
