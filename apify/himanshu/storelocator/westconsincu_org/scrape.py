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
    base_url = "https://www.westconsincu.org"
    r = session.get("https://www.westconsincu.org/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    address_object = {}
    for script in soup.find_all("script"):
        if "var locationList = " in script.text:
            location_list = json.loads(script.text.split("var locationList = ")[1].split("}];")[0] + "}]")
            for i in range(len(location_list)):
                address_object[location_list[i]["name"]] = location_list[i]
    names = []
    for location in soup.find("div",{'class':"table page large home-cta"}).find_all("div",{'class':"cell"}):
        if location.find("h2") == None:
            continue
        if location.find("h2").text in names:
            continue
        names.append(location.find("h2").text)
        name = location.find("h2").text
        location_details = list(location.find('div',{'class':'text-box'}).stripped_strings)[:-1]
        for i in range(len(location_details)):
            if location_details[i] == "Phone:":
                phone = location_details[i+1]
                break
        for i in range(len(location_details)):
            if "Hours" in location_details[i]:
                hours = " ".join(location_details[i+1:])
                break
        store = []
        store.append("https://www.westconsincu.org")
        store.append(location_details[0])
        store.append(address_object[location_details[0]]['address'])
        store.append(address_object[location_details[0]]['city'])
        store.append(address_object[location_details[0]]['state'])
        store.append(address_object[location_details[0]]['zip'])
        store.append("US")
        store.append(address_object[location_details[0]]['idx'])
        store.append(phone)
        store.append("west consin credit union")
        store.append(address_object[location_details[0]]['coordLat'])
        store.append(address_object[location_details[0]]['coordLong'])
        store.append(hours.replace("\u2010"," "))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
