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
    base_url = "https://rossy.ca"
    r = session.get("https://rossy.ca/magasins/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "var wpgmaps_localize_marker_data = " in script.text:
            location_list = json.loads(script.text.split("var wpgmaps_localize_marker_data = ")[1].split("};")[0] + "}")
            for key in location_list:
                for key1 in location_list[key]:
                    store_data = location_list[key][key1]
                    hours_phone = list(BeautifulSoup(store_data["desc"],"lxml").stripped_strings)
                    store_data["address"] = store_data["address"].replace(", Canada","").replace(", Canad\u00e1","")
                    if len(store_data["address"].split(",")) == 3:
                        if len(store_data["address"].split(" ")[-3]) == 2:
                            store_data["address"] = store_data["address"][:-8] + "," + store_data["address"][-8:]
                    if len(store_data["address"].split(",")) == 2:
                        store_data["address"] = store_data["address"][:-8] + "," + store_data["address"][-8:]
                        city = store_data["address"].split(",")[0].split(" ")[-1]
                        store_data["address"] = store_data["address"].replace(city,"," + city)
                    store = []
                    store.append("https://rossy.ca")
                    store.append(store_data['title'])
                    if " ".join(store_data["address"].split(",")[0:-3]) == "":
                        if len(store_data["address"].split(",")[-1]) == 8:
                            store.append(store_data['address'].split(",")[0])
                            store.append("<MISSING>")
                            store.append(store_data['address'].split(",")[1])
                            store.append(store_data['address'].split(",")[2])
                        else:
                            store.append(store_data['address'].split(",")[0])
                            store.append(store_data['address'].split(",")[1])
                            store.append(store_data['address'].split(",")[2])
                            store.append("<MISSING>")
                    else:
                        store.append(" ".join(store_data["address"].split(",")[0:-3]))
                        store.append(store_data['address'].split(",")[-3])
                        store.append(store_data['address'].split(",")[-2])
                        store.append(store_data["address"].split(",")[-1][1:])
                    store.append("CA")
                    store.append(key1)
                    store.append(hours_phone[0].replace("T:",""))
                    store.append("rossy")
                    store.append(store_data["lat"])
                    store.append(store_data["lng"])
                    store.append(" ".join(hours_phone[1:]))
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
