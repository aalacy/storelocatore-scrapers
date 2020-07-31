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
    base_url = "https://apoyo-financiero.com"
    page_url = "https://apoyo-financiero.com/en/sucursales.html"
    r = session.post(base_url + "/sucursales.json")
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        
        location_name = "apoyo-financiero at - " + store_data['name']
        raw_address = store_data['address'].split(",")
        raw_street = raw_address[0].split(' ')
        # print(raw_street)

        if "Fontana" or "Fresno" or "Norwalk" in raw_street:
            st = " ".join(raw_street[0:-1])
        else:
            st = "".join(raw_street)

        if raw_street[-2] == "#":
            st2 = st + " 3"
        else:
            st2 = st


        street_address = st2.replace("West","").replace(" Santa","")
        city = store_data['name'].split('-')[0]
        raw_phone = str(store_data['tel'])
        phone = "(" + raw_phone[:3] + ") " + raw_phone[3:6] + "-" + raw_phone[6:]
        store = []
        store.append("https://apoyo-financiero.com")
        store.append(location_name)
    
        store.append(street_address)
        store.append(city)
        if len(store_data['address'].split(",")[-1].split(" ")) == 4:
            store.append(store_data['address'].split(",")[-1].split(" ")[-3])
            store.append(store_data["address"].split(",")[-1].split(" ")[-1])
        else:
            store.append(store_data['address'].split(",")[-1].split(" ")[-2])
            store.append(store_data["address"].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("apoyo financiero")
        store.append(store_data["lat"])
        store.append(store_data["lon"])
        store.append("<MISSING>")
        store.append(page_url)

        # store.append(store_data['address'].split(",")[0])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
