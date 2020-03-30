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
    base_url = "https://www.esso.ca/en/api/v1/Retail/retailstation/GetStationsByBoundingBox?Latitude1=16.698659791445607&Latitude2=36.22597707315531&Longitude1=-76.07080544996313&Longitude2=-119.57666482496313"
    r = session.get(base_url).json()
    return_main_object = []
    for esso in r:
        store = []
        store.append("https://www.esso.ca")
        store.append(esso['DisplayName'])
        store.append(esso['AddressLine1'])
        store.append(esso['City'])
        try:
            store.append(esso['StateProvince'])
        except:
            store.append("<MISSING>")
        try:
            store.append(esso['PostalCode'])
        except:
            store.append("<MISSING>")
        if esso['Country']=="Canada":
            store.append("CA")
        else:
            store.append(esso['Country'])
        store.append("<MISSING>")
        if esso['Telephone']:
            store.append(esso['Telephone'])
        else:
            store.append("<MISSING>")
        store.append("Esso")
        store.append(esso['Latitude'])
        store.append(esso['Longitude'])
        store.append(esso['WeeklyOperatingDays'].replace('<br/>',','))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
