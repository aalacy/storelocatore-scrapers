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
    base_url = "https://subaru.ca/"
    soup = bs(session.get("https://subaru.ca/Map/DealerFeed.aspx?latitude=62.536041259765625&longitude=-96.38835144042969&maxRadius=10000&numResults=1000&WebSiteID=282").text, "lxml")
    
    for mark in soup.find_all("marker"):
        
        location_name = mark['name']
        
        street_address = mark['address1']
        city = mark['city']
        state = mark['provincecode']
        zipp = mark['postalcode'].upper()
        store_number = mark['id']
        phone = mark['phone'].split("---")[0].split(",")[0].split("-toll-free")[0].split("--")[0].replace("1AWD-","")
        lat = mark['latitude']
        lng = mark['longitude']
        page_url = mark['href']
        

        sales = ''
        service = ''
        parts = ''
        for hr in mark.find('hours').find_all("time"):
            sales+= " "+ hr['dayname']+" "+ hr['sales'] + " "
            service+= " "+ hr['dayname']+" "+ hr['service'] + " "
            parts+= " "+ hr['dayname']+" "+ hr['parts'] + " "
        
        hours = "Sales Hour : "+ sales.strip() +" Service Hour : "+ service.strip() +" Parts Hour : "+ parts.strip()
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("CA")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
        yield store
       
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()