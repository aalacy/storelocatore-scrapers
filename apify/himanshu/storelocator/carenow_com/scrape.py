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
    base_url = "https://www.carenow.com"
    r = session.get("https://core.secure.ehc.com/src/tools/services/locations-controller.dot?serviceId=&host=08d5f8fe-16dc-4326-89c5-dc78ed4d8219&facilityUrl=&pullFrom=Facility&pullFromHost=Auto&marketId=&starRatings=true&showOnly=Urgent_Care&state=&region=&division=&tag=&facilityTags=").json()
    return_main_object = []
    for location in r['Locations']:
        if location['Address1']: 
            cleanr = re.compile('<.*?>')
            hour = re.sub(cleanr, ' ', location['Hours'])
            hour=re.sub(r'\s+', ' ', hour).strip()
            store=[]
            store.append(base_url)
            store.append(location['Title'])
            store.append(location['Address1'])
            store.append(location['City'])
            store.append(location['State'])
            store.append(location['Zip'])
            store.append("US")
            store.append(location['Coid'])
            if location['PrimaryPhone']:
                store.append(location['PrimaryPhone'])
            else:
                store.append("<MISSING>")
            store.append("carenow")
            store.append(location['Latitude'])
            store.append(location['Longitude'])
            if hour:
                store.append(hour.strip())
            else:
                store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
