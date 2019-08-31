import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.thriftyfoods.com"
    r = requests.get("https://www.thriftyfoods.com/api/en/Store/get?Latitude=48.45423&Longitude=-123.359205&Skip=0&Max=60000000").json()
    return_main_object = []
    for loc in r['Data']:
        hour=loc['OpeningHours'].strip()
        name=loc['Name'].strip()
        address=loc['AddressMain']['Line'].strip()
        zip=loc['AddressMain']['DisplayPostalCode'].strip()
        city=loc['AddressMain']['City'].strip()
        state=loc['AddressMain']['Province'].strip()
        lat=loc['Coordinates']['Latitude']
        lng=loc['Coordinates']['Longitude']
        phone=loc['PhoneNumberHome']['Number']
        country="CA"
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("thriftyfoods")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
