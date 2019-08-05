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
    base_url = "http://www.relaxandwax.com"
    dt='lat=33.4052217&lng=-86.87547819999998&radius=1000'
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    r = requests.post(base_url+"/GoogleMaps/store_locator.php",data=dt,headers=headers).json()
    return_main_object = []
    for loc in r:
        store=[]
        hour=''
        madd=loc['address'].split(',')
        city="<INACCESSIBLE>"
        if len(madd)==1:
            madd=loc['address'].strip().split(' ')
            zip=madd[-1].strip()
            state=madd[-2].strip()
            del madd[-1]
            del madd[-1]
            address=' '.join(madd).strip()
        elif len(madd)==3:
            address=madd[0].strip()
            city=madd[-2].strip()
            state=madd[-1].strip().split(' ')[0].strip()
            zip=madd[-1].strip().split(' ')[1].strip()
        else:
            address=madd[0].strip()
            st=madd[1].strip().replace(' - ',' ').split(' ')
            state=st[-2].strip()
            zip=st[-1].strip()
            if len(st)>3:
                state=st[-2].strip()
                zip=st[-1].strip()
                del st[-1]
                del st[-2]
                city=' '.join(st).strip()
        store.append(base_url)
        store.append(loc['name'].strip())
        store.append(address.strip())
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append(loc['id'])
        if loc['telephone']:
            store.append(loc['telephone'])
        else:
            store.append("<MISSING>")
        store.append("relaxandwax")
        store.append(loc['lat'])
        store.append(loc['lng'])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
