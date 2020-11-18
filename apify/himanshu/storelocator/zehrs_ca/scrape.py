import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'site-banner': 'fortinos',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        }
    base_url = "https://www.zehrs.ca/"
    
    r = session.get("https://www.zehrs.ca/api/pickup-locations?bannerIds=zehrs",headers=headers).json()
    for val in r:
        store_number = val['id'].replace("CT","").replace("0096SD1179","0096SD1268")
        time.sleep(2)
        jd = session.get("https://www.zehrs.ca/api/pickup-locations/"+store_number,headers=headers).json()
        city=''
        state =''
        zipp =''
        street_address=''
        location_name=''
        hours_of_operation =''
        if "name" in jd:
            
            location_name = jd['name']
            
            if val['address']['line2']!=None:
                if "address" in jd:
                    street_address = jd['address']['line1']+" "+jd['address']['line2']
            else:
                street_address = jd['address']['line1']
            if "address" in jd:
                city = jd['address']['town']
                state = jd['address']['region']
                if jd['address']['postalCode']!=None:
                    zipp = jd['address']['postalCode']
                else:
                    zipp = "<MISSING>"
            location_type=''
            latitude=''
            longitude=''
            if "location_type" in jd:
                location_type = jd['locationType']
                latitude = jd['geoPoint']['latitude']
                longitude = jd['geoPoint']['longitude']
                
            page_url = "https://www.zehrs.ca/api/pickup-locations/"+store_number
            if 'storeDetails' in jd:
                phone = jd['storeDetails']['phoneNumber']
                hoo = []
                
                # print(jd['storeDetails']['storeHours'])
                for h in jd['storeDetails']['storeHours']:
                    if h['day'] == None or h['hours']== None:
                        frame=""
                    else:
                        frame = h['day']+"-"+h['hours']
                    hoo.append(frame)
                hours_of_operation = ", ".join(hoo)
            else:
                phone = "<MISSING>"
                hours_of_operation = "<MISSING>"
            store = []
            store.append(base_url if base_url else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append("CA")
            store.append(store_number)
            store.append(phone if phone else '<MISSING>')
            store.append(location_type)
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            store = [x.strip() if type(x) == str else x for x in store]
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2]=="<MISSING>" and store[3]=="<MISSING>" and store[4]=="<MISSING>" and store[5]=="<MISSING>":
                continue
            # print(store)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
