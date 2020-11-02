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
    base_url = "https://www.firstam.com"
    r = session.get("https://www.firstam.com/services-api/api/alta/search?take=100000&skip=0&officeDisplayFlag=true&officeZipCode=&officeStatus=active",verify=False)
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.firstam.com")
        store.append(store_data['officeName'])
        if store_data["officeAddressLine1"] == None:
            continue
        store.append(store_data["officeAddressLine1"] + store_data["officeAddressLine2"] if store_data["officeAddressLine2"] != None else store_data["officeAddressLine1"])
        store.append(store_data['officeCity'])
        store.append(store_data['officeState'])
        store.append(store_data["officeZipCode"].replace(".","").strip() if store_data["officeZipCode"] != "" and store_data["officeZipCode"] != None else "<MISSING>")
        store.append("US")
        store.append(store_data['officeId'])
        store.append(store_data['officePhoneAreaCode'] + " " + store_data['officePhoneNumber'] if store_data['officePhoneAreaCode'] != None else "<MISSING>")
        store.append(store_data['companyName'] if store_data['companyName'] != None else store[1])
        store.append(store_data["officeLatitude"] if store_data["officeLatitude"] != None else "<MISSING>")
        store.append(store_data["officeLongitude"] if store_data["officeLongitude"] != None else "<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
