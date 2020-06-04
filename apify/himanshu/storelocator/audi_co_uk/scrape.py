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
    base_url = "https://www.audi.co.uk/"
    json_data = session.get("https://soa.audi.co.uk/audi-dealercentre-service/dealerservice/getdealerlist?dealerCentreType=D&dealerCentreType=SD").json()
    
    for data in json_data:
        
        location_name = data['name']
        street_address = ''

        if data['mainAddress']['address1']:
            street_address+= data['mainAddress']['address1']
        if data['mainAddress']['address2']:
            street_address+= data['mainAddress']['address2']
        if data['mainAddress']['address3']:
            street_address+= " "+ data['mainAddress']['address3']
        city = data['mainAddress']['town']
        state = data['mainAddress']['county']
        zipp = data['mainAddress']['postcode']
        store_number = data['dealerCode']
        phone = data['telephone']
        lat = data['mainAddress']['latitude']
        lng = data['mainAddress']['longitude']
        page_url = data['url']
        
        
        hours = ''
        for hr in data['services']:
            if 'serviceOpeningHours' in hr:
                for hrs in hr['serviceOpeningHours']:
                    if 'open' in hrs:
                        hours+= " "+ hrs['day']+" "+datetime.strptime(hrs['open'],"%H:%M").strftime("%I:%M %p")+"-"+datetime.strptime(hrs['close'],"%H:%M").strftime("%I:%M %p")
                    else:
                        hours+= " "+hrs['day']+ " Closed"
             
        
        
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("GB")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
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
