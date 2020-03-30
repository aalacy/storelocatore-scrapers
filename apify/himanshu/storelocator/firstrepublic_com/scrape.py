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
    base_url = "https://www.firstrepublic.com"
    r = session.get( base_url + "/Location/GetOfficeJsonSitecore")
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.firstrepublic.com")
        store.append(store_data['Name'])
        store.append(store_data["Address1"] + store_data["Address2"])
        store.append(store_data['City'])
        store.append(store_data['State'])
        store.append(store_data["Zip"])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["PrimaryPhone"])
        store.append("first public")
        store.append(store_data["Latitude"])
        store.append(store_data["Longitude"])
        location_reqeust = session.get(base_url + store_data["FriendlyUrl"])
        location_soup = BeautifulSoup(location_reqeust.text,"lxml")
        store.append(" ".join(list(location_soup.find("div",{"class":'location-detail--section location-detail__hours'}).stripped_strings)))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
