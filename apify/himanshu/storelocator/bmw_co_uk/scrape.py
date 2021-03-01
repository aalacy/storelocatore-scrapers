


import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bmw_co_uk')


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
    MAX_RESULTS = 100
    MAX_DISTANCE = 20
    base_url = "https://www.bmw.co.uk/"

    search = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN],
                              max_radius_miles = MAX_DISTANCE,
                              max_search_results = MAX_RESULTS)
    for coord in search:
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        
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
            
            search.found_location_at(lat,lng)

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
        
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store

    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
