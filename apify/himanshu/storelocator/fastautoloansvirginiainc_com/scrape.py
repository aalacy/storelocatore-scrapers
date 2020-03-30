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
    base_url = "https://fastautoloansvirginiainc.com"
    r = session.get(base_url + "/closest-stores?loan_type=all&num=0")
    data = r.json()["locations"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://fastautoloansvirginiainc.com")
        store.append(store_data['business_name'])
        store.append(store_data["address_line_1"] + store_data["address_line_2"] if store_data["address_line_2"] != None else store_data["address_line_1"])
        store.append(store_data['locality'])
        store.append(store_data['administrative_area'])
        store.append(store_data["postal_code"])
        store.append(store_data["country"])
        store.append(store_data["id"])
        store.append(store_data["primary_phone"])
        store.append("fast auto loans")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        if store_data["monday_hours"] == None and store_data["tuesday_hours"] and store_data["wednesday_hours"]:
            continue
        else:
            if store_data["monday_hours"] != None:
                hours = hours + str(store_data["monday_hours"])
            if store_data["tuesday_hours"] != None:
                hours = hours + str(store_data["tuesday_hours"])
            if store_data["wednesday_hours"] != None:
                hours = hours + str(store_data["wednesday_hours"])
            if store_data["thursday_hours"] != None:
                hours = hours + str(store_data["thursday_hours"])
            if store_data["friday_hours"] != None:
                hours = hours + str(store_data["friday_hours"])
            if store_data["saturday_hours"] != None:
                hours = hours + str(store_data["saturday_hours"])
            if store_data["sunday_hours"] != None:
                hours = hours + str(store_data["sunday_hours"])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
