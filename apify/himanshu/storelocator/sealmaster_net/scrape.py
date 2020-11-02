import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://sealmaster.net"
    location_url= "https://sealmaster.net/?hcs=locatoraid&hca=search%3Asearch%2F85029%2Fproduct%2F_PRODUCT_%2Flat%2F%2Flng%2F%2Flimit%2F100%2Fradius%2F250"
    r = session.get(location_url, headers=headers).json()
    for i in r["results"]:
        location_name = (i['name'])
        store_number = i["id"]               
        latitude = i['latitude']       
        longitude = i['longitude']            
        street_address = (str(i['street1']+" "+str(i['street2'])))        
        city = (i['city'])            
        zipp = (i['zip'])
        state = (i['state'])  
        phone = (i['phone'])              
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>" )
        store.append("<MISSING>")
        store.append( latitude if latitude else "<MISSING>")
        store.append( longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://sealmaster.net/locations/")
        yield store
      
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
