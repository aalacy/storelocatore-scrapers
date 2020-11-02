import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
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
    
    base_url = "https://intersport.com/"
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'fr-CA',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    json_data = session.get("https://www.sportsexperts.ca/api/fglstore/getallstoreslisting", headers=headers).json()['Stores']
    
    
    for data in json_data:
        
        
        location_name = data['StoreName']
        street_address = data['Address']['Line1']
        if "Line2" in data:
            if data['Address']['Line2']:
                street_address += " "+ data['Address']['Line2']
        city = data['Address']['City']
        state = data['Address']['RegionCode']
        zipp = data['Address']['PostalCode']
        country_code = data['Address']['CountryCode']
        phone = data['PhoneNumber']
        store_number = data['StoreNumber']
        location_type = "Store"
        lat = data['Address']['Latitude']
        lng = data['Address']['Longitude']
        hours = ""

        for label in data['OpeningHours']['OpeningHoursByDay']:
            if label['StartingTime']:
                hours += " " +label['DaySEO']+ " "+datetime.strptime(label['StartingTime'],"%H:%M").strftime("%I:%M %p")+" - "+datetime.strptime(label['EndingTime'],"%H:%M").strftime("%I:%M %p")+" "
            else:
                hours += " " + label['DaySEO']+ " Closed"
        page_url = "https://www.sportsexperts.ca" + data['StoreUrl']
                
        
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours.strip())
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
