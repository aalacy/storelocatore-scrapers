import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    credentials_request = requests.get("https://www.76.com/bin/stationfinderservlet?s=psx_76",headers=headers)
    credential = credentials_request.json()["credentials"]
    return_main_object = []
    addresses = []
    cords = sgzip.coords_for_radius(200)
    for cord in cords:
        base_url = "https://www.76.com"
        r = requests.get("https://spatial.virtualearth.net/REST/v1/data/a1ed23772f5f4994a096eaa782d07cfb/US_BrandedSites/Sites?spatialFilter=nearby(" + str(cord[0]) + ","+ str(cord[1]) + ",200.00)&$filter=Brand%20eq%20%27U76%27&$format=json&$inlinecount=allpages&$select=*,__Distance&key=" + credential + "&$top=1000",headers=headers)
        data = r.json()["d"]["results"]
        for store_data in data:
            store = []
            store.append("https://www.76.com")
            store.append(store_data["Name"])
            store.append(store_data["AddressLine"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["Locality"])
            store.append(store_data["AdminDistrict"])
            # some time mexico locations were coming but the country was written as US
            if len(store[-1]) != 2:
                continue
            store.append(store_data["PostalCode"])
            store.append(store_data["CountryRegion"])
            store.append(store_data["EntityID"])
            store.append(store_data["Phone"] if store_data["Phone"] else "<MISSING>")
            store.append("76")
            store.append(store_data["Latitude"])
            store.append(store_data["Longitude"])
            store.append("<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
