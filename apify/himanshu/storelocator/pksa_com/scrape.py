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
    base_url = "https://pksa.com"
    r = session.get("https://pksa.com/franchise/pksa-locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_object = {}
    for script in soup.find_all("script"):
        if 'var locations = ' in script.text:
            location_list = json.loads(re.sub("(\w+):", r'"\1":',script.text.split('var locations = ')[1].split("}, ];")[0] + "}]"))
            for i in range(len(location_list)):
                geo_object[location_list[i]['label'].replace("PKSA ","")] = location_list[i]["position"]
    for location in soup.find_all("div",{"class":'col-md-3'}):
        location_details = list(location.stripped_strings)
        if location_details == []:
            continue
        if "(" in location_details[1] and ")" in location_details[1]:
            del location_details[1]
        if len(location_details[2].split(",")) != 2:
            location_details[1] = " ".join(location_details[1:3])
            del location_details[2]
        store = []
        store.append("https://pksa.com")
        store.append(location_details[0])
        if len(location_details[2].split(",")) != 2:
            store.append(" ".join(location_details[1].split(" ")[:-3]))
            store.append(location_details[1].split(" ")[-3])
            store.append(location_details[1].split(" ")[-2].replace(".",""))
            store.append(location_details[1].split(" ")[-1])
        else:
            store.append(location_details[1])
            store.append(location_details[2].split(",")[0])
            store.append(location_details[2].split(",")[1].split(" ")[1].replace(".",""))
            store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        for i in range(len(location_details)):
            if location_details[i] == "Phone:":
                phone = location_details[i+1]
                break
        store.append("<MISSING>")
        store.append(phone)
        store.append("pksa")
        if location_details[0] in geo_object:
            store.append(geo_object[location_details[0]]["lat"])
            store.append(geo_object[location_details[0]]["lng"])
            del geo_object[location_details[0]]
        else:
            for key in geo_object:
                if location_details[0] in key:
                    store.append(geo_object[key]["lat"])
                    store.append(geo_object[key]["lng"])
                    del geo_object[key]
                    break
        store.append("<MISSING>")
        if len(store) < 12:
            for key in geo_object:
                if store[1] in key:
                    store.append(geo_object[key]["lat"])
                    store.append(geo_object[key]["lng"])
                    del geo_object[key]
                    break
        return_main_object.append(store)
    for location in soup.find_all("div",{"class":'col-md-4'}):
        location_details = list(location.stripped_strings)
        if location_details == []:
            continue
        if len(location_details[3].split(",")) != 2:
            location_details.insert(0,"extra text")
        store = []
        store.append("https://pksa.com")
        store.append(location_details[1])
        store.append(location_details[2])
        store.append(location_details[3].split(",")[0])
        store.append(location_details[3].split(",")[1].split(" ")[1])
        store.append(location_details[3].split(",")[1].split(" ")[-1])
        store.append("US")
        for i in range(len(location_details)):
            if location_details[i] == "Phone:":
                phone = location_details[i+1]
                break
        store.append("<MISSING>")
        store.append(phone)
        store.append("pksa")
        if location_details[0] in geo_object:
            store.append(geo_object[location_details[0]]["lat"])
            store.append(geo_object[location_details[0]]["lng"])
            del geo_object[location_details[0]]
        else:
            for key in geo_object:
                if location_details[0] in key:
                    store.append(geo_object[key]["lat"])
                    store.append(geo_object[key]["lng"])
                    del geo_object[key]
                    break
        if len(store) < 12:
            for key in geo_object:
                if store[1] in key:
                    store.append(geo_object[key]["lat"])
                    store.append(geo_object[key]["lng"])
                    del geo_object[key]
                    break
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()