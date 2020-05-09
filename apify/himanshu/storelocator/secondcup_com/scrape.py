import csv
from bs4 import BeautifulSoup
import re
import sgzip
import json
import time
from sgrequests import SgRequests
import unicodedata
session = SgRequests()
import requests

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["CA"])
    MAX_RESULTS = 100
    MAX_DISTANCE =1
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    base_url = "https://secondcup.com"

    while zip_code:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        headers = {
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'content-type':'application/x-www-form-urlencoded',
            'origin':'https://secondcup.com',
            'referer':'https://secondcup.com/find-a-cafe',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
        data = {
            "postal_code":str(zip_code),
            "honeypot_time":"Ech6g3iMi-H6Z4jue6vfKvtnbaIuyYaIvYUFbqGLSOk",
            "form_build_id":"form-Ew0fgdBS1W2ylO2VK6tOdFIZ8cytvafKxI0jfcerTSk",
            "form_id": "postal_code_form",
            "url":""
        }
        location_url = "https://secondcup.com/find-a-cafe"
        r = requests.post(location_url, data=data, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        current_results_len = len(soup.find_all("a",{"class":"a-link"}))
        for link in soup.find_all("a",{"class":"a-link"}):
            if "google" in link['href']:
                continue
            page_url = base_url+link['href']
            # print(page_url)

            r1 = requests.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find("div",{"class":"l-location__title"}).text.strip()
            addr = list(soup1.find("div",{"class":"m-location-features__address"}).stripped_strings)
            print(addr)
            if addr:
                street_address = addr[0]
                city = addr[1].split(",")[0]
                # if "Orlans" == city.strip():
                #     city = "Orleans"
                state = addr[1].split(",")[1]
                zipp = addr[1].split(",")[2].strip()
            else:
                street_address ="<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
            phone = re.sub(r'\s+'," ",soup1.find("div",{"class":"m-location-features__phone"}).text.replace("ext. 21079","").split("/")[0].replace("TBD","<MISSING>").replace("No Phone","<MISSING>"))
            if phone == " ":
                phone = "<MISSING>"
            else:
                phone = phone
            hours = " ".join(list(soup1.find("ul",{"class":"m-location-hours__list"}).stripped_strings))

            result_coords.append((0, 0))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("CA")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("Cafe")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours)
            store.append(page_url)
            if (str(store[1])+" "+str(store[2])+" "+str(store[-1])) in addresses:
                continue
            addresses.append(str(store[1])+" "+str(store[2])+" "+str(store[-1]))
            
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [str(x).replace("\xe2","-").replace("\xe7",'') if x else "<MISSING>" for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
            yield store
            
            # print("data == " + str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")    
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



