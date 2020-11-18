import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time 
from sgrequests import SgRequests
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('mitsubishicars_com')
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url ="https://www.mitsubishicars.com/"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    addressess =[]
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    while zip_code:
        result_coords = []
        try:
            link = "https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode="+str(zip_code)+'&idealer=false&ecommerce=false'
            json_data = session.get(link, headers=headers).json()
        except:
            pass
        current_results_len = len(json_data)  
        for loc in json_data:
            address = loc['address1'].strip()
            if loc['address2']:
                address+=' '+loc['address2'].strip()
            name = loc['dealerName'].strip()
            city = loc['city'].strip().capitalize()
            state = loc['state'].strip()
            zipp = loc['zipcode']
            phone = loc['phone'].strip()
            country = loc['country'].replace("United States","US").strip()
            lat = loc['latitude']
            lng = loc['longitude']
            link = loc['dealerUrl'] 
            storeno = loc['bizId']
            if link:
                page_url = "http://"+link.lower()
                # logger.info(page_url)
                if "http://www.verneidemitsubishi.com" in page_url or "http://www.kingautomitsubishi.com" in page_url or "http://www.verhagemitsubishi.com" in page_url or "http://www.sisbarro-mitsubishi.com" in page_url or "http://www.delraymitsu.net" in page_url:
                    hours_of_operation = "<INACCESSIBLE>"
                else:
                    try:
                        r1 = session.get(page_url, headers=headers)
                    except:
                        pass
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    if soup1.find("div",{"class":"sales-hours"}):
                        hours_of_operation = " ".join(list(soup1.find("div",{"class":"sales-hours"}).stripped_strings))
                    elif soup1.find("ul",{"class":"list-unstyled line-height-condensed"}):
                        hours_of_operation = " ".join(list(soup1.find("ul",{"class":"list-unstyled line-height-condensed"}).stripped_strings))
                    elif soup1.find("div",{"class":"well border-x"}):
                        hours_of_operation = " ".join(list(soup1.find("div",{"class":"well border-x"}).find("table").stripped_strings))
                    elif soup1.find("div",{"class":"hours-block pad-2x"}):
                        hours_of_operation = " ".join(list(soup1.find("div",{"class":"hours-block pad-2x"}).stripped_strings))
                    elif soup1.find("div",{"class":"hoursBox"}):
                        hours_of_operation = " ".join(list(soup1.find("div",{"class":"hoursBox"}).stripped_strings))
                    else:
                        hours_of_operation = "<INACCESSIBLE>"
            else:
                hours_of_operation = "<MISSING>"
            if city == "Little rock" or city == "Charlottesville":
                page_url = "<MISSING>"
            result_coords.append((lat,lng))
            store=[]
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country)
            store.append(storeno)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()       
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
