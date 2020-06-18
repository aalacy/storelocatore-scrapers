import csv
from sgrequests import SgRequests
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import time
session = SgRequests()

def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    MAX_RESULTS = 60
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    
    base_url = "https://www.kia.com/"
    
    while zip_code:
        result_coords =[]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        location_url = "https://www.kia.com/us/services/en/dealers/search"

        data = r'{"type":"zip","zipCode":"'+str(zip_code)+'","dealerCertifications":[],"dealerServices":[]}'
        try:
            json_data = session.post(location_url, data=data).json()
        except:
            pass
        for store in json_data:
            
            location_name = store['name']
            street_address = store['location']['street1']
            city = store['location']['city']
            state = store['location']['state']
            zipp = store['location']['zipCode']
            phone = "<INACCESSIBLE>"
            lat = store['location']['latitude']
            lng = store['location']['longitude']
            store_number = store['code'].replace(state,"")
            page_url = store['url'].lower()
            hours = ""
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
            hours = "<MISSING>"
            hours='<INACCESSIBLE>'
            try:
                store_soup = request_wrapper(page_url.lower(),"get",headers=headers)
            except:
                pass

            # try:
            #     if store_soup.find("div",{"class":"row info-row"}):
            #         hours = " ".join(list(store_soup.find("div",{"class":"row info-row"}).find_all("div")[-1].stripped_strings))
            #     elif store_soup.find("div",{"id":"hours1-app-root"}):
            #         hours = " ".join(list(store_soup.find("div",{"id":"hours1-app-root"}).find("ul").stripped_strings))
            #     elif store_soup.find("div",{"class":"col-xs-12 col-sm-6 col-md-3 hours-col"}):
            #         hours = " ".join(list(store_soup.find_all("div",{"class":"col-xs-12 col-sm-6 col-md-3 hours-col"})[1].stripped_strings)) + \
            #             " ".join(list(store_soup.find_all("div",{"class":"col-xs-12 col-sm-6 col-md-3 hours-col"})[2].stripped_strings))
            #     elif store_soup.find("dl",{"itempro":"openingHoursSpecification"}):
            #         hours = " ".join(list(store_soup.find("dl",{"itempro":"openingHoursSpecification"}).stripped_strings))
            #     else:
            #         hours = "<MISSING>"
            # except:
                # pass
    
            result_coords.append((lat,lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours else "<MISSING>")
            store.append(page_url)     
            if store[2] in adressess:
                continue
            adressess.append(store[2]) 
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            yield store
            # print(store)
             
        if len(json_data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
