# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import re
import json
import unicodedata
from sgrequests import SgRequests
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addressess = []
    headers = {
            'authority': "www.cartersoshkosh.ca",
            'method': 'GET',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language':'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application / x - www - form - urlencoded;charset= UTF - 8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }
    base_url = "https://www.cartersoshkosh.ca/"
    location_url = "https://www.cartersoshkosh.ca/on/demandware.store/Sites-CartersCA-SFRA-Site/en_CA/Stores-GetNearestStores?postalCode=A1A&countryCode=CA&distanceUnit=imperial&maxdistance=1000000&lat=47.5702401&lng=-52.69563350000001"
    r = session.get(location_url, headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    # print(soup)
    json_data = r.json()
    for key,value in json_data['stores'].items():
        # print(value.keys())
        store_number = value['storeid']
        # print(value)
        location_name = "Carter's OshKosh"+" "+str(value['mallName'])
        # print(location_name)
        street_address = value['address1']+" "+value['address2']
        city = value['city']
        zipp  = value['postalCode']
        country_code = value['countryCode']
        phone = value['phone']
        latitude = value['latitude']
        longitude = value['longitude']
        state = value['stateCode']
        hours_of_operation =(' sun ' +value["sundayHours"] + ' mon ' +value["mondayHours"]+ ' Tues ' +value["tuesdayHours"]+ ' Wed ' +value["wednesdayHours"]+ ' Thurs ' +value["thursdayHours"]+ ' Fri ' +value["fridayHours"]+ ' Sat ' +value["saturdayHours"]).strip()
        locator_domain = base_url
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("<MISSING>")
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation )
        store.append("<MISSING>")
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
