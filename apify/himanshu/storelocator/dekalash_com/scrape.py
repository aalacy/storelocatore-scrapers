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
    base_url = "https://dekalash.com"
    r = session.get("https://dekalash.com/find-a-studio",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "studioList " in script.text:
            location_list = json.loads(script.text.split("studioList = ")[1].split("!= null ?")[0])
            comming_soon_list = json.loads(script.text.split("futureStudioList = ")[1].split("!= null ?")[0])
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://dekalash.com")
                store.append(store_data["DisplayName"])
                store.append(store_data["Address1"] + " " + store_data["Address2"] if store_data["Address2"] != None else store_data["Address1"])
                store.append(store_data["City"])
                store.append(store_data["StateAbbr"])
                store.append(store_data["Zip"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["Phone"].split("or")[0] if store_data["Phone"] != None else "<MISSING>")
                store.append("deka lash")
                store.append(store_data['Latitude'])
                store.append(store_data['Longitude'])
                location_request = session.get(base_url + store_data["DetailPageUrl"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                hours = " ".join(list(location_soup.find("div",{"class":re.compile("day-list")}).stripped_strings)).replace("\n"," ").replace("\r"," ").replace("\t"," ")
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
            for i in range(len(comming_soon_list)):
                store_data = comming_soon_list[i]
                store = []
                store.append("https://dekalash.com")
                store.append(store_data["DisplayName"])
                store.append(store_data["Address1"] + " " + store_data["Address2"] if store_data["Address2"] != None else store_data["Address1"])
                store.append(store_data["City"])
                store.append(store_data["StateAbbr"])
                store.append(store_data["Zip"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["Phone"].split("or")[0] if store_data["Phone"] != None else "<MISSING>")
                store.append("deka lash")
                store.append(store_data['Latitude'])
                store.append(store_data['Longitude'])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
