


import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
import sgzip
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
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['gb'])
    MAX_RESULTS = 100
    MAX_DISTANCE = 20
    coord = search.next_coord()
    base_url = "https://www.bmw.co.uk/"

    while coord:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        
        result_coords = []
        json_data = session.get("https://discover.bmw.co.uk/proxy/api/dealers?q="+str(coord[0])+","+str(coord[1])+"&type=new").json()
        
        
        for data in json_data:
            if "message" in data:
                continue
            
            location_name = data['dealer_name']
            street_address = ''

            if data['address_line_1']:
                street_address+= data['address_line_1']
            if data['address_line_2']:
                street_address+= " "+data['address_line_2']
            if data['address_line_3']:
                street_address+= " "+ data['address_line_3']
            city = data['town']
            state = data['county']
            zipp = data['postcode']
            store_number = data['id']
            phone = data['primary_phone']
            lat = data['latitude']
            lng = data['longitude']
            page_url = data['url']
           
            if page_url:
                
                if page_url == "https://www.buchananbmw.co.uk" or page_url == "https://www.ridgewaysalisburybmw.co.uk" or page_url == "https://www.bmwparklane.com":
                    hours = "<MISSING>"
                else:
                    try:
                        soup = bs(session.get(page_url+"/contact-us/").text, "lxml")
                        hours = " ".join(list(soup.find("section",{"class":"opening-hours"}).stripped_strings)).replace("Opening Hours","").strip()
                    except:
                        soup = bs(session.get(session.get(page_url+"/contact-us/").url + "/contact-us/").text , "lxml")
                        hours = " ".join(list(soup.find("section",{"class":"opening-hours"}).stripped_strings)).replace("Opening Hours","").strip()
            else:
                hours = "<MISSING>"
            
            result_coords.append((lat,lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(re.sub(r"\s+"," ",street_address).strip())
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("UK")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     
        
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
        if len(json_data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
