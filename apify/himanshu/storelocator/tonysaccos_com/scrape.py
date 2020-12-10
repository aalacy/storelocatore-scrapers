import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
import itertools
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://tonysaccos.com"
    r = session.get(base_url +'/locations/' , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    frame = soup.find_all("div",{"class":"wpb_column vc_column_container vc_col-sm-6"})[::2]
    iframe = soup.find_all("iframe")
    for (i,j) in zip(frame,iframe):
        dl = list(i.stripped_strings)
        if len(dl)==10:
            location_name=dl[1]+" - "+dl[0].lower()
            street_address = dl[2]
            addr = dl[3].split(" ")
            city = addr[0]
            state = addr[1]
            zipp = addr[2]
            phone = dl[5]
            hours_of_operation = ",".join(dl[7:])
        elif len(dl)==12:
            location_name=dl[1]+" - "+dl[0].lower()
            street_address = ",".join(dl[3:5])
            addr = dl[5].split(" ")
            city = addr[0]
            state = addr[1]
            zipp = addr[2]
            phone = dl[7]
            hours_of_operation = ",".join(dl[9:])
        elif len(dl)==11:
            location_name=dl[1]+" - "+dl[0].lower()
            street_address = dl[2]
            city = dl[3].split(",")[0]
            state = dl[3].split(",")[1].strip().split(" ")[0]
            zipp = dl[3].split(",")[1].strip().split(" ")[1]
            phone = dl[5]
            hours_of_operation = ",".join(dl[7:])
        elif len(dl)==9:
            location_name=dl[1]+" - "+dl[0].lower()
            street_address = dl[2]
            city = dl[3].split(",")[0]
            state = dl[3].split(",")[1].strip().split(" ")[0]
            zipp = dl[3].split(",")[1].strip().split(" ")[1]
            phone = dl[5]
            hours_of_operation = ",".join(dl[7:])
        map_url = j['src'].split("!2d")[1].split("!2m3!")[0].split("!3d")
        lat = map_url[1]
        lng = map_url[0]

        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("<MISSING>")
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append("https://tonysaccos.com/locations/")
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()