import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }
    base_url = "https://www.dicarlospizza.com"
    # r =  session.get("https://www.dicarlospizza.com/locations", headers=headers)
    json_url = "https://www.dicarlospizza.com/app/store/api/v10/editor/users/127469322/sites/693050464538353041/store-locations?page=1&per_page=100&include=address&lang=en"
    json_data = session.get(json_url,headers=headers).json()
    for value in json_data['data']:
        if "COLUMBUS" in value['display_name']:
            continue
        
        location_name = value['display_name']
        street_address = value['address']['data']['street']
        city = value['address']['data']['city']
        state = value['address']['data']['region_code']
        zipp = value['address']['data']['postal_code']
        country_code = "US"
        store_number = "<MISSING>"
        phone = value['address']['data']['phone']
        location_type = "<MISSING>"
        latitude = value['address']['data']['latitude']
        longitude = value['address']['data']['longitude']
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        if location_name == "HILLIARD":
            page_url = "https://www.dicarlospizza.com/s/order?location=11e9d659db2a733bb2160cc47a2ae638"

        if location_name =="AKRON":
            page_url = "https://www.dicarlospizza.com/s/order?location=11e9faa4aad5901b9fa50cc47a2ae330"

        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name.lower() if location_name.lower() else '<MISSING>')
        store.append(street_address.lower() if street_address.lower() else '<MISSING>')
        store.append(city.lower() if city.lower() else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


    location_url = "https://www.dicarlospizza.com/locations"
    r = session.get(location_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    json_data2 = json.loads(str(soup).split("window.__BOOTSTRAP_STATE__ = ")[1].split(";")[0])
    inst = json_extract(json_data2, 'insert')
    remove_list = ['LOGIN',' \n','\n',' ','\ufeff','LOCATIONS','OHIO','640 PORTAGE TRAIL EXT W','234.716.1769','AKRON\n','\ufeff\ufeff','SOUTH CAROLINA','PENNSYLVANIA','WEST VIRGINIA','COMING SOON\n','000.000.0000','HIGHLANDS\n','304.','4142 MAIN ST','614.777.4992﻿','HILLIARD\n','91 E 5TH STREET','614.966.2055﻿','COLUMBUS\n','WASHINGTON','724.624.5420\ufeff','925 JEFFERSON AVE']
    res = filter(lambda i: i not in remove_list, inst)
    raw_data = list(res)
    final_data = [raw_data[i:i+3] for i in range(0, len(raw_data), 3)]

    for i in final_data:
        street_address = i[0].replace("\n","")
        phone = i[1].replace("737.9849","304.737.9849").replace("845.9295","304.845.9295").replace("\ufeff","")
        location_name = i[2].replace('\n',"")
        city = location_name
        ohio = ['BELMONT','ST CLAIRSVILLE','STEUBENVILLE','TORONTO']
        if city in ohio:
            state = "OH"
        elif "MYRTLE BEACH" in city:
            state = "SC"

        else:
            state = "WV"
        
        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name.lower() if location_name.lower() else '<MISSING>')
        store.append(street_address.lower() if street_address.lower() else '<MISSING>')
        store.append(city.lower() if city.lower() else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append('<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
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




