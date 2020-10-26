import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tenethealth_com')


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
    # addresses = []
    # r_headers = {
    #     'Accept': '*/*',
    #     'Content-Type': 'application/json; charset=UTF-8',    
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    # }
    base_url = "https://www.tenethealth.com"
    r = session.get("https://www.tenethealth.com/api/facilities/GetFacilities").json()

    addressesess=[]
    CountryCode = "US"
    for anchor in r['Facilities']:
        location_name = anchor['Title']
        page_url = anchor['WebsiteUrl']
        if "CountryCode" in anchor:
            if anchor["CountryCode"] != "US" or anchor["CountryCode"] != "CA":
                continue
        street_address = anchor['Address']['Street']
        if "Suite" in street_address:
            street_address = street_address.split("Suite")[0].replace(",","").strip()
        if "suite" in street_address:
            street_address = street_address.split("suite")[0].replace(",","").strip()
        if "Ste" in street_address:
            street_address = street_address.split("Ste")[0].strip()
        city = anchor['Address']['City']
        state = anchor['Address']['StateCode']
        zipp = anchor['Address']['Zip']
        phone = anchor['PhoneNumber']
        if "FacilityClassName" in anchor:
            location_type = anchor['FacilityClassName']
        else:
            location_type = "<MISSING>"
        latitude = anchor['Address']['Latitude']
        longitude = anchor['Address']['Longitude']
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append(CountryCode)
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        # store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressesess:
            continue
        addressesess.append(store[2])
        # logger.info("data == "+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
