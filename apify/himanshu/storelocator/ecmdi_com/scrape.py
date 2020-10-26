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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "upgrade-insecure-requests": "1",
        "Referer": "https://www.ecmdi.com/"
        }
    base_url = "https://www.ecmdi.com"
    r = session.get("https://www.ecmdi.com/storelocator/index/storeSearch/?lat=40.7226698&lng=-73.51818329999998&radius=12000",headers=headers)
    #print(r.text)
    data = r.json()["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.ecmdi.com")
        store.append(store_data['branch_name'])
        store.append(store_data["branch_add1"] + store_data["branch_add2"])
        store.append(store_data['branch_city'])
        store.append(store_data['branch_state'])
        store.append(store_data["brnach_zip"])
        store.append("US")
        store.append(store_data['branch_id'])
        store.append(store_data['branch_phone'])
        store.append("east coast metal distributors")
        store.append(store_data["lattitude"])
        store.append(store_data["longitude"])
        hours = ""
        if store_data["branch_mon_open"] and store_data["branch_mon_open"] != "":
            hours = hours + " Monday open time " + store_data["branch_mon_open"] +" Monday close time " + store_data["branch_mon_close"] + " "
        if store_data["branch_tue_open"] and store_data["branch_tue_open"] != "":
            hours = hours + " tuesday open time " + store_data["branch_tue_open"] +" tuesday close time " + store_data["branch_tue_close"] + " "
        if store_data["branch_wed_open"] and store_data["branch_wed_open"] != "":
            hours = hours + " wednesday open time " + store_data["branch_wed_open"] +" wednesday close time " + store_data["branch_wed_close"] + " "
        if store_data["branch_thu_open"] and store_data["branch_thu_open"] != "":
            hours = hours + " thursday open time " + store_data["branch_thu_open"] +" thursday close time " + store_data["branch_thu_close"] + " "
        if store_data["branch_fri_open"] and store_data["branch_fri_open"] != "":
            hours = hours + " friday open time " + store_data["branch_fri_open"] +" friday close time " + store_data["branch_fri_close"] + " "
        if store_data["branch_sat_open"] and store_data["branch_sat_open"] != "":
            hours = hours + " saturday open time " + store_data["branch_sat_open"] +" saturday close time " + store_data["branch_sat_close"] + " "
        if store_data["branch_sun_open"] and store_data["branch_sun_open"] != "":
            hours = hours + " sunday open time " + store_data["branch_sun_open"] +" sunday close time " + store_data["branch_sun_close"] + " "
        if hours == "":
            hours = "<MISSING>"
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
