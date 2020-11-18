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
    
    base_url = "https://www.pizzaexpress.com"

  
    json_data = session.get("https://www.pizzaexpress.com/api/Restaurants/FindRestaurantsByLatLong?latitude=51.50732&longitude=-0.12764746&searchTerm=London%2C%20City%20of%20London%2C%20United%20Kingdom&pageNumber=1&limit=2000").json()
    
    
    for data in json_data:
        
        
        location_name = data['name']
        street_address = data['Address1']
        city = data['Location']
        state = data['Region'].strip()
        zipp = data['Postcode']
        country_code = "UK"
        phone = data['phone']
        store_number = data['restaurantId']
        location_type = "Restaurant"
        lat = data['latitude']
        lng = data['longitude']
        hours = ""

        for label in data['openingHours']:
            hours += " " +label['label']+ " "+label['value']+" "    
        
        page_url = base_url + data['link']
        
        
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
    
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
        
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
