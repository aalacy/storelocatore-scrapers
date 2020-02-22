import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
session = SgRequests()
import requests
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    search.initialize(country_codes=["US"])
    MAX_RESULTS = 300
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        base_url = "https://www.napaonline.com"
        headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        'accept': 'text/html, */*; q=0.01'
        }
        #print("https://www.napaonline.com/en/store-finder?q="+str(zip_code)+"&sort=true")
     
        r = requests.get("https://www.napaonline.com/en/store-finder?q="+str(zip_code)+"&sort=true", headers=headers)
       
        soup = BeautifulSoup(r.text, "lxml")
        latitude = []
        longitude = []
        if soup.find("div", {"id":"map_canvas"}) != None:
            json_data = json.loads(soup.find("div", {"id":"map_canvas"})['data-stores'])
            
            for i in range(len(json_data)):
                latitude.append(json_data['store'+str(i)]['latitude'])
                longitude.append((json_data['store'+str(i)]['longitude']))

        current_results_len = len(soup.find_all("div",{"class":"pure-g"}))
        for index,data in enumerate(soup.find_all("div",{"class":"pure-g"})):
            page_url = base_url + data.find("a",{"class":"storeWebsiteLink"})['href']
            location_name = re.sub(r'\s+'," ",data.find("a",{"class":"storeWebsiteLink"}).text)
            street_address = (data.find("div",{"class":"address-1"}).text + str(data.find("div",{"class":"address-2"}).text)).strip()
            addr = re.sub(r'\s+'," ",(data.find_all("div",{"class":"address-2"})[-1].text)).replace("Punta Gorda, FL, FL 33950","Punta Gorda, FL 33950")
            city = addr.split(",")[0]
            state = addr.split(",")[1].split(" ")[1]
            zipp = addr.split(",")[1].split(" ")[2]
            store_number = page_url.split("/")[-1]
            phone = re.sub(r'\s+'," ",data.find("div",{"class":"phone"}).text)
            location_type = "Auto Parts"
            hours = " ".join(list(data.find("div",{"class":"store-hours"}).stripped_strings)).replace('Shop this Store','').strip()


            
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
            store.append(location_type)
            store.append(latitude[index])
            store.append(longitude[index])
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data ====="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store

        # print(current_results_len)
        if current_results_len < MAX_RESULTS:
                # print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

