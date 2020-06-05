import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    address = []
    coords = sgzip.coords_for_radius(200)
    for coord in coords:
        r = session.get("https://www.desigual.com/on/demandware.store/Sites-dsglcom_prod_us-Site/en_US/Address-SearchStoreAddress?&deliveryPoint=STORE&radius=100000&showOfficialStores=false&showOutlets=false&showAuthorized=false&showOnlyAllowDevosStores=false")
        data = r.json()
        mp = data['shippingAddresses']
        for i in data['shippingAddresses']:
            if i["countryCode"] not in ["US","CA"]:
                continue
            if 'address' in i:
                street_address = i['address']
            else:
                street_address = "<MISSING>"
            if 'name' in i:
                loacation_name = i['name']
            else:
                loacation_name = "<MISSING>"
            if 'city' in i:
                city = i['city']
            else:
                city = "<MISSING>"
            if 'region' in i:
                state = i['region']
            else:
                state = "<MISSING>"
            if 'postalCode' in i:
                zipp =i['postalCode']
            else:
                zipp = "<MISSING>"
            if 'latitude' in i:
                latitude = i['latitude']
            else:
                latitude = "<MISSING>"
            if 'countryCode' in i:
                country_code = i['countryCode']
            else:
                country_code = "<MISSING>"
            if 'longitude' in i:
                longitude = i['longitude']
            else:
                longitude = "<MISSING>"
            if 'storeId' in i:
                store_number = i['storeId']
            else:
                store_number = "<MISSING>"
            if 'phone' in i:
                phone = i['phone']
            else:
                phone = "<MISSING>"
            hours = ""
            days = {1:"Sunday",2:"Monday",3:"Tuesday",4:"Wednesday",5:"Thursday",6:"Friday",7:"Saturday"}
            if "schedule" in mp and mp["schedule"]:
                store_hours = mp["schedule"]
                for hour in store_hours:
                    hours = hours + " " + days[hour["dayNumber"]] + " " + hour["value"]
                store.append(hours)
            store = []
            store.append("https://www.desigual.com/")
            store.append(loacation_name if loacation_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours if hours else "<MISSING>")
            store.append("<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
