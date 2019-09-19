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
    base_url = "https://www.luckybrand.com"
    headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36","Authorization": "R8-Gateway App=shoplocal, key=luckybrand, Type=SameOrigin","Geo-Position": "30.7876;-116.06","X-Device-Id": "4ca26032-fc4d-b686-d862-d1c5303512e7","X-Domain-Id": "luckybrand"}
    r = requests.get("https://luckybrand.radius8.com/api/v1/streams/stores?lat=30.7876&lng=-116.06&radius=10000&units=MI&limit=10000&_ts=1563881553972",headers=headers).json()
    return_main_object = []
    for val in r['results']:
        address=val['address']['address1']
        if "address2" in val['address'].keys():
            if val['address']['address2']:
                address+=val['address']['address2']
        city=val['address']['city']
        if "state" in val['address'].keys():
            state=val['address']['state']
        else:
            state="<MISSING>"
        zip=val['address']['postal_code']
        if "contact_info" in val:
            if "phone" in val['contact_info']:
                phone=val['contact_info']['phone']
            else:
                phone="<MISSING>"
        else:
            phone="<MISSING>"
        country=val['address']['country']
        if country=="USA":
            country="US"
        elif country=="CAN":
            country="CA"
        lat=val['geo_point']['lat']
        lng=val['geo_point']['lng']
        hour=""
        for hr in val['hours']:
            if val:
                hour+=hr+":"+'-'.join(val['hours'][hr])+" "
        name=val['name']
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append(country)
        store.append("<MISSING>")
        store.append(phone)
        store.append("luckybrand")
        store.append(lat)
        store.append(lng)
        if hour:
            store.append(hour)
        else:
            store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
