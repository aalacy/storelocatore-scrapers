import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import cgi
import sgzip



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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    current_results_len = 0 
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        
        base_url= "https://familythriftcenter.com/wp-content/plugins/store-locator/sl-xml.php?mode=gen&lat="+ str(lat)+"&lng="+str(lng)+"&radius=500"
        try:
            r = session.get(base_url)
        except:
            continue
        soup= BeautifulSoup(r.text,"lxml")
        
        link = soup.find_all("marker")
        
        for i in link:
            location_name = (i.attrs['name'])
            street_address = (i.attrs['street'])
            city = (i.attrs['city'])
            state = (i.attrs['state'])
            zipp = (i.attrs['zip'])
            phone = (i.attrs['phone'])
            latitude = (i.attrs['lat'])
            longitude = (i.attrs['lng'])
            hours_of_operation = (i.attrs['hours'].replace("\r","").replace("\n","").replace("~","-"))
            store = []
            store.append("https://familythriftcenter.com/")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(base_url)
            if store[2] in addresses :
                    continue
            addresses.append(store[2])
            yield store
            #print("--------------------",store)
            
        if current_results_len < MAX_RESULTS:
            
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
