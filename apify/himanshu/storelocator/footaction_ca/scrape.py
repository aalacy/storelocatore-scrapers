import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
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
    base_url = "https://www.footaction.ca/"
    r = session.get(base_url , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for i in soup.find_all("div", {"class":"store-container"}):
        dl = list(i.stripped_strings)
        
        location_name = dl[0]
        street_address = dl[1]
        city = dl[2].split(",")[0]
        temp_state = dl[2].split(",")[1].strip().split(" ")
        if len(temp_state) == 3:                            # state = dl[2].split(",")[1].strip().split(" ")[0]
            state = temp_state[0]
            zipp = " ".join(temp_state[1:])
        else:
            state = '<MISSING>'
            zipp = dl[2].split(",")[1].strip()
        
        phone = dl[3].strip()
        hours_of_operation = ", ".join(list(i.find("div", {"class":"store-hours"}).stripped_strings))
        map_url = i.find('a', href=True)['href']
        lat = map_url.split('@')[1].split(',')[0]
        lng = map_url.split('@')[1].split(',')[1]
   
       
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("CA")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Foot Action")
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append("<MISSING>")
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()