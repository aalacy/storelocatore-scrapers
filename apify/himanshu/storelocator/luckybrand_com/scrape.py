import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['us', 'ca'])

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": "R8-Gateway App=shoplocal, key=luckybrand, Type=SameOrigin",
    "Connection": "keep-alive",
    "Cookie": "r8d=6445a34d-455d-f094-0e82-872f195dce4b; r8lsc_luckybrand_shoplocal=40613",
    "Host": "luckybrand.radius8.com",
    "Referer": "https://luckybrand.radius8.com/sl/shoplocal?r8dref=6445a34d-455d-f094-0e82-872f195dce4b&",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "X-Device-Id": "6445a34d-455d-f094-0e82-872f195dce4b",
    "X-Domain-Id": "luckybrand",
    "X-Request-Tag": "rsQhlMGgA5WZx773hlUsrlS/sNklkVDFoas5cQy36JQBAFEx/5InLVjTdGASEV3Dcym7EfhoCsZOlWGJvrtLcw==#NDY4NzQ1"
}

def fetch_data():
    return_main_object = []
    base_url = "https://www.luckybrand.com"
    coord = search.next_coord()
    keys = set()
    while coord:
        print('{} zip codes remaining'.format(len(search.zipcodes)))
        result_coords = []
        ts = int(round(time.time() * 1000))
        query_lat, query_lng = coord[0], coord[1]
        r = session.get("https://luckybrand.radius8.com/api/v1/streams/stores?lat={}&lng={}&radius=1000&units=MI&limit=50&_ts={}".format(query_lat, query_lng, ts),headers=HEADERS)
        parsed = r.json()
        for val in parsed['results']:
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
            result_coords.append((lat, lng))
            hour='<MISSING>'
            if 'hours' in val:
                hour = ''
                for hr in val['hours']:
                    if val:
                        hour+=hr+":"+'-'.join(val['hours'][hr])+" "
            name=val['name'] if 'name' in val else '<MISSING>'
            page_url = val['landingPageUrl'] if 'landingPageUrl' in val else '<MISSING>'
            store=[]
            store.append(base_url)
            store.append(page_url)
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
            key = '|'.join([address, city, state, zip])
            if key not in keys:
                return_main_object.append(store)
                keys.add(key)
        if len(result_coords) > 0:
            search.max_count_update(result_coords)
        else:
            search.max_distance_update(100)
        coord = search.next_coord()
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
