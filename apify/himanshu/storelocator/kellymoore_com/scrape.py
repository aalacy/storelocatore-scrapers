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
    base_url = "https://kellymoore.com"
    r = session.get(base_url + "/wp-json/storelocator/_GetAllStores")
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://kellymoore.com")
        store.append(store_data['StoreName'])
        store.append(store_data["Address"])
        store.append(store_data['City'])
        store.append(store_data['State'])
        if store_data['State'] == "AK":
            continue
        store.append(store_data["ZipCode"])
        store.append("US")
        store.append(store_data["StoreId"])
        store.append(store_data["PhoneNumber"])
        store.append("<MISSING>")
        store.append(store_data["Latitude"])
        store.append(store_data["Longitude"])
        hours = ""
        if store_data["MondayHours"] != None and store_data["MondayHours"] != "":
            hours = hours + " MondayHours " +str(store_data["MondayHours"]) + " "
        if store_data["TuesdayHours"] != None and store_data["TuesdayHours"] != "":
            hours = hours + " TuesdayHours " +str(store_data["TuesdayHours"]) + " "
        if store_data["WednesdayHours"] != None and store_data["WednesdayHours"] != "":
            hours = hours + " WednesdayHours " +str(store_data["WednesdayHours"]) + " "
        if store_data["ThursdayHours"] != None and store_data["ThursdayHours"] != "":
            hours = hours + " ThursdayHours " +str(store_data["ThursdayHours"]) + " "
        if store_data["FridayHours"] != None and store_data["FridayHours"] != "":
            hours = hours + " FridayHours " +str(store_data["FridayHours"]) + " "
        if store_data["SaturdayHours"] != None and store_data["SaturdayHours"] != "":
            hours = hours + " SaturdayHours " +str(store_data["SaturdayHours"]) + " "
        if store_data["SundayHours"] != None and store_data["SundayHours"] != "":
            hours = hours + " SundayHours " +str(store_data["SundayHours"]) + " "
        store.append(hours.replace('Hours','') if hours != "" else "<MISSING>")
        store.append('<MISSING>')
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
