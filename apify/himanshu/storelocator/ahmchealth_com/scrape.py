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
    
    base_url = "https://www.ahmchealth.com/"

    soup = bs(session.get("https://www.ahmchealth.com/map/").content, "lxml")

    for cols in soup.find_all("div",{"class":"g-cols wpb_row offset_small vc_inner"})[:11]:
        location = list(cols.stripped_strings)
        
        if location:
            location_name = location[0]
            
            if len(location[1].split(",")) == 3:
                
                street_address = location[1].split(",")[0]
                city = location[1].split(",")[1]
            else:
                street_address = " ".join(location[1].split(",")[0].split()[:-1]).replace("Monterey","").replace("South El","").replace("San","")
                city = location[1].split(",")[0].split()[-1].replace("Monte","South El Monte").replace("Park","Monterey Park").replace("Gabriel","San Gabriel")
                
            state = location[1].split(",")[-1].split()[0]
            zipp = location[1].split(",")[-1].split()[1]
            phone = location[2]
            page_url = cols.find_all("a")[-1]['href']
           
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(page_url)     
        
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            yield store
        else:
            continue
       
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
