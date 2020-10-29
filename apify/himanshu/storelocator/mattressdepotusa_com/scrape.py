
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mattressdepotusa_com')


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
    data = session.get("https://www.mattressdepotusa.com/wp-admin/admin-ajax.php?action=store_search&lat=47.60621&lng=-122.332071&max_results=500&search_radius=500&autoload=10000",headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).json()
    for data in (data):
        Suite=''
        address2=''
        if "address2" in data:
            Suite =data['address2']
            if Suite:
                address2 = Suite
                

        street_address =data['address']+ ' ' +address2
        location_name = data["store"]
        city = data['city']
        zipp = data['zip']
        state = data['state']
        phone = data['phone']
        longitude =data['lng']
        latitude =data['lat']
        page_url = data['permalink']
        
        hours=''
        hours =  " ".join(list(bs(data['hours'],'lxml').stripped_strings))
       
        store_number = "<MISSING>"
        store = []
        store.append("https://www.mattressdepotusa.com/")
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
        # if store[2] in addresses:
        #     continue
        # addresses.append(store[2])
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",store)
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
