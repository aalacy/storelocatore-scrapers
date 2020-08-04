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
    base_url = "https://eatphillysbest.com"
    r = session.get("https://eatphillysbest.com/store-locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_object = {}
    for script in soup.find_all("script"):
        if 'address_objects.push(' in script.text:
            for location in script.text.split('address_objects.push(')[1:]:
                location_details = json.loads(location.split(");")[0].replace('[,]','["<MISSING>","<MISSING>"]'))
                geo_object[location_details["Title"]] = location_details["LatLng"]
    for location in soup.find("div",{'id':"all_locations"}).find_all("li"):
        phone = list(location.stripped_strings)[-1]
        page_url = base_url + location.find("a")["href"]        
        location_request = session.get(base_url + location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,'lxml')
        location_details = list(location_soup.find("div",{'id':'location_address'}).stripped_strings)[:-1]
        if len(location_details[3].split(" ")[-1]) == 5:
            location_details[1] = " ".join(location_details[1:3])
            del location_details[2]
        store = []
        store.append("https://eatphillysbest.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[1].split(" ")[1])
        store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append(location.find("a")["href"].split("/")[-2])
        store.append(phone)
        store.append("philly's")
        store.append(geo_object[location_details[0]][0])
        store.append(geo_object[location_details[0]][1])
        store.append(location_details[-1] if "Tel" not in location_details[-1] else "<MISSING>")

        # r1 = session.get("https://eatphillysbest.com/store-locations/",headers=headers)
        # soup1 = BeautifulSoup(r1.text,"lxml")
        # for link in soup1.find('div',{'id':'all_locations'}).find_all('li'):
        #     page_url
        store.append(page_url)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
