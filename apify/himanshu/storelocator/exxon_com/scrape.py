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
    base_url = "https://www.exxon.com/en/api/v1/Retail/retailstation/GetStationsByBoundingBox?Latitude1=16.698659791445607&Latitude2=36.22597707315531&Longitude1=-76.07080544996313&Longitude2=-119.57666482496313"
    r = session.get(base_url).json()
    return_main_object = []
    for location in r:
        store = []
        store.append("https://www.exxon.com")
        store.append(location['DisplayName'].strip())
        store.append(location['AddressLine1'].strip())
        store.append(location['City'].strip())
        store.append(location['StateProvince'].strip())
        store.append(location['PostalCode'].strip())
        if location['Country']=='United States':
            store.append('US')
        else:
            store.append(location['Country']) 
        store.append(location['LocationID'].strip())
        if location['Telephone']:
            store.append(location['Telephone'].strip())
        else: 
            store.append("<MISSING>")
        store.append("exxon")
        store.append(location['Latitude'])
        store.append(location['Longitude'])
        if location['WeeklyOperatingDays']:
             store.append(location['WeeklyOperatingDays'].replace('<br/>',','))
        else: 
            store.append("<MISSING>")
       
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
