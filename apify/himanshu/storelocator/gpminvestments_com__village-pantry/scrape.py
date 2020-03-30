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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    base_url = "https://gpminvestments.com/village-pantry"
    r = session.get("https://gpminvestments.com/store-locator/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = "action=wpgmza_sl_basictable&security=fc0b57223a&map_id=7"
    for state in soup.find_all("a",{"name":re.compile("marker")}):
        data = data + "&marker_array%5B%5D=" + state["name"].replace("marker","")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    r = session.post("https://gpminvestments.com/wp-admin/admin-ajax.php",headers=headers,data=data)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find("div").find_all("div",recursive=False):
        geo_location = location.find("a",text="Directions")["gps"]
        location_details = list(location.stripped_strings)
        state_split = re.findall("([A-Z]{2})",location_details[1].replace("USA",""))
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_details[1])
        if store_zip_split:
            store_zip = store_zip_split[-1]
        else:
            store_zip = "<MISSING>"
        location_details[1] = location_details[1].replace(location_details[0],"").replace("\t"," ")
        store = []
        store.append("https://gpminvestments.com")
        store.append(location_details[0])
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append(location["mid"])
        store.append("<MISSING>") # phone
        store.append("<MISSING>") # location_type
        store.append(geo_location.split(",")[0])
        store.append(geo_location.split(",")[1])
        store.append("<MISSING>") # hours_of_operation
        store.append("<MISSING>") # page_url
        store.append(location_details[1].replace(state,"").replace(store_zip,"").replace(", , United States","").replace("  "," ").replace(", , USA",""))
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()