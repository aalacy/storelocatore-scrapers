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

def convert_time(time):
    temp_time = str(time)[:-2] + ":" + str(time)[-2:]
    is_am = "AM"
    hour = int(str(time)[:-2])
    if int(hour) < 12:
        is_am = "AM"
        hour = int(str(time)[:-2])
    else:
        is_am = "PM"
        hour = int(str(time)[:-2]) - 12
    return str(hour) + ":" + str(time)[-2:] + " " + is_am

def fetch_data():
    headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://bonanzasteakhouses.com"
    r = session.get("https://locations.pon-bon.com/locations.json",headers=headers)
    return_main_object = []
    location_data = r.json()["locations"]
    for store_data in location_data:
        if store_data["loc"]["country"] not in ["US","CA","PR"]:
            continue
        store = []
        store.append("https://bonanzasteakhouses.com")
        store.append(store_data["loc"]["customByName"]["Geomodifier"])
        store.append(store_data["loc"]["address1"] + " " + store_data["loc"]["address2"])
        store.append(store_data["loc"]["city"])
        store.append(store_data["loc"]["state"] if store_data["loc"]["state"] else store_data["loc"]["country"])
        store.append(store_data["loc"]["postalCode"])
        store.append(store_data["loc"]["country"] if store_data["loc"]["country"] != "PR" else "US")
        store.append(store_data["loc"]["id"])
        store.append(store_data["loc"]["phone"])
        store.append("<MISSING>")
        store.append(store_data["loc"]["latitude"])
        store.append(store_data["loc"]["longitude"])
        store_hours = store_data["loc"]['hours']["days"]
        hours = ""
        for i in range(len(store_hours)):
            if store_hours[i]["intervals"] == []:
                hours = hours + " " + store_hours[i]["day"] + " CLOSED"
            else:
                hours = hours + " " + store_hours[i]["day"] + " " + convert_time(store_hours[i]['intervals'][0]["start"]) + " - " + convert_time(store_hours[i]['intervals'][0]["end"])
        if hours.count("CLOSED") > 5:
            continue
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        store = [x.strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
