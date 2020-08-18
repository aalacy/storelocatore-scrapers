
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
    data = session.get("https://www.compassus.com/locations.json?api=location_browser",headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).json()
    for data in data:
        if "primary_address" in data:
            address2=''
            if "second_line" in data['primary_address']:
                if data['primary_address']['second_line']:
                    address2= data['primary_address']['second_line']
            street_address =data['primary_address']["first_line"]+' '+address2
            location_name = data["name"]
            city = data['primary_address']['city']
            zipp = data['primary_address']['postal_code']
            state = data['primary_address']['state']
            longitude =data['primary_address']['lng']
            latitude =data['primary_address']['lat']
            page_url = "https://www.compassus.com"+(data['url'])
            phone = (bs(data['primary_address']['phone_number_assignments'][0]['number'],"lxml").find("a",{"class":"telephone-link"}).text.strip())
            hours= "<MISSING>"
            store_number = "<MISSING>"
            store = []
            store.append("https://www.codeninjas.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url if page_url else "<MISSING>")     
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip().replace("0.000000","<MISSING>").replace("(248) 865-4148 / 4444",'(248) 865-4148') if x else "<MISSING>" for x in store]
    
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",store)
            yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
