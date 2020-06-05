
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    addresses = []
    base_url = "https://www.toyota.co.uk/"

    # print("remaining zipcodes: " + str(len(search.zipcodes)))
    result_coords = []
    soup = session.get("https://www.toyota.co.uk/api/dealer/drive/-0.1445783/51.502436?count=1000&extraCountries=im|gg|je&isCurrentLocation=false").json()
    for data in soup['dealers']:
        street_address1=''
        location_name = data['name']
        street_address1 = data['address']['address1'].strip()
        if street_address1:
            street_address1=street_address1

        street_address =street_address1+ ' '+ data['address']['address'].strip()
        city = data['address']['city']
        state = data['address']['_region'].replace('Co. ','').strip()
        zipp = data['address']['zip']
        phone = data['phone']
        if "geo" in  data['address']:
            lat = data['address']['geo']['lat']
            lng = data['address']['geo']['lon']
        else:
            lat ="<MISSING>"
            lng ="<MISSING>"
        page_url = data['url']
        store_number = "<MISSING>"
        hours="<MISSING>"
        try:
            hours = " ".join(list(bs(session.get(page_url+"/about-us#anchor-views-opening_hours-block_3").content, "lxml").find("div",{"class":"views-row views-row-1 views-row-odd views-row-first views-row-last zero-dep"}).stripped_strings))
        except:
            hours="<MISSING>"
        
        result_coords.append((lat,lng))
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
