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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {
        'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        }
    return_main_object = []
    base_url = "https://mandarinrestaurant.com/"
    get_url ='https://mandarinrestaurant.com/wp-admin/admin-ajax.php?action=store_search&lat=43.73155&lng=-79.76242&max_results=40&search_radius=50&autoload=1'
    json_data = session.get(get_url,headers = header).json()
    for value in json_data:
        location_name = value['store']
        street_address = value['address']
        city = value['city']
        state = value['state']
        zipp = value['zip']
        country_code = "CA"
        store_number = value['id']
        phone = value['phone']
        location_type = "<MISSING>"
        latitude = value['lat']
        longitude = value['lng']
        hours_of_operation = value['hours'].replace('\n',"").replace("<p>","").replace("<br />"," ").replace("</p>","").replace("</span>"," ").replace("<span>","").replace("&amp;",",")
        page_url = value['url']



        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('CA')
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store
    
        
  
def scrape():
    # fetch_data()
    data = fetch_data()    
    write_output(data)

scrape()
