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
    base_url = "http://vino100.com"
    r = session.get("http://vino100.com/locations.fx",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    address = []
    for state in soup.find("select",{"name":"state_select"}).find_all("option",{"style":"color:#000000;"}):
        for script in soup.find_all("script"):
            if 'stateData' in script.text:
                data = script.text.split("stateData['"+ state["value"] +"'] = ")[1].split(";")[0].replace("'","")
                location_details = list(BeautifulSoup(data,"lxml").stripped_strings)[:-1]
                locations = []
                for i in range(len(location_details)):
                    if location_details[i] == "\\":
                        temp_location = []
                        for k in range(i+1,len(location_details)):
                            if location_details[k] == "\\":
                                locations.append(temp_location)
                                break
                            elif k == len(location_details) - 1:
                                temp_location.append(location_details[k])
                                locations.append(temp_location)
                                break
                            temp_location.append(location_details[k])
                for i in range(len(locations)):
                    location_details = locations[i]
                    store = []
                    store.append("http://vino100.com")
                    store.append(location_details[0])
                    store.append(" ".join(location_details[1:-2]))
                    store.append(location_details[0].split(",")[0])
                    store.append(location_details[0].split(",")[-1])
                    store.append("<MISSING>")
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(location_details[-2].replace("(VINO)",""))
                    store.append("vino 100")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
