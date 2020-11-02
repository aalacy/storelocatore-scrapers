import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
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
    base_url = "https://cinnabon.ca/"
    location_url= "https://cinnabon.ca/wp-admin/admin-ajax.php?action=store_search&lat=43.65323&lng=-79.38318&max_results=75&search_radius=50&autoload=1"
    r = session.get(location_url, headers=headers).json()
    for i in r:
        store_number = i["id"]
        location_name = i['store']            
        latitude = i['lat']       
        longitude = i['lng']            
        street_address =(i['address2'])    
        city = (i['city'])            
        zipp = (i['zip'])
        state = (i['state'])  
        phone = (i['phone'])
        country_code = i['country'] 
        location_type =  i['address']  
        mp  = i['hours'] 
        hours_of_operation = mp.replace("</time></td></tr><tr><td>",", ").replace("</td><td><time>"," - ").split("<td>")[1].split("</time>")[0]
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>" )
        store.append( location_type if location_type else "<MISSING>")
        store.append( latitude if latitude else "<MISSING>")
        store.append( longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else"<MISSING>")
        store.append("https://cinnabon.ca/locations/")
        yield store
     
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
