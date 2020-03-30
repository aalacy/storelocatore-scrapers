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
    base_url = "https://www.infiniti.ca"
    r = session.get("https://www.infiniti.ca/infinitiretailers/locate/retailersAjax?channelCode=in&zipCode=M4B%201T4&format=json",headers=headers)
    return_main_object = []
    location_data = r.json()['retailers']
    for store_data in location_data:
        store = []
        store.append("https://www.infiniti.ca")
        store.append(store_data["name"])
        store.append(store_data["addressLine1"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zipCode"][:3] + " " + store_data["zipCode"][3:])
        store.append("CA")
        store.append("<MISSING>")
        store.append(store_data["phoneNumber"])
        store.append("infiniti")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        for key in store_data:
            if "Hours" in key:
                store_hours = store_data[key]
                hours = hours + " " + key
                for hour_key in store_hours:
                    if store_hours[hour_key]["startingHour"] == "0000" and store_hours[hour_key]["closingHour"] == "0000":
                        hours = hours + " " + store_hours[hour_key]["days"] + " Closed "
                    else:
                        hours = hours + " " + store_hours[hour_key]["days"] + " " + convert_time(store_hours[hour_key]["startingHour"]) + " - " + convert_time(store_hours[hour_key]["closingHour"])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
