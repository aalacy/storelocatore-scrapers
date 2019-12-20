import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
import time
import sgzip
import pprint


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
    base_url = "https://publicstoragecanada.com"
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    # print("====")
    MAX_RESULTS = 51
    MAX_DISTANCE = 50
    current_results_len = 0 
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "x-requested-with":"XMLHttpRequest",
        "referer": "https://www.thetinfishrestaurants.com/locations-menus/find-a-tin-fish-location-near-you/",
        "content-type" :"application/x-www-form-urlencoded; charset=UTF-8",
    }
    coord = search.next_zip()
    while coord:
        # print("================",coord)
        count = 0
        result_coords =[]
        locator_domain = "https://publicstoragecanada.com"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "CA"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ''
        # print("==============",str(search.current_zip))
        # "N4W"
        # data1 = "useCookies=1&lang=&q=A1A+1A1&searchBranch=1&searchATM=1"
        data = 'action=search_locations_ajax&location=+'+str(coord)
        try:
            data = requests.post("https://publicstoragecanada.com/wp-admin/admin-ajax.php",headers=headers,data=data).json()
        except:
            pass
        # except:
        #     continue
        if type(len(data['data']))==int:
            current_results_len = len(data['data'])
            
        for loc in data['data']:
            # soup= BeautifulSoup(loc["address"],"lxml")
            city_state_zipp = loc["address"].split(",<br/>")[-1]
            street_address = loc["address"].split(",<br/>")[0].replace(",",' ')
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(city_state_zipp))
            state_list = re.findall(r' ([A-Z]{2})', str(city_state_zipp))
            city = city_state_zipp.split(',')[0]
            
            page_url = loc['link']
            location_name = loc['title']

            r1 = requests.get(page_url,headers=headers,data=data)
            soup1= BeautifulSoup(r1.text,"lxml")
            
            hours = re.sub(r"\s+", " ", soup1.find("div",class_='singleLocationOfficeHours marginB30').text)
            hours1 = re.sub(r"\s+", " ", soup1.find("div",class_='singleLocationGateHours').text)
            hours_of_operation = hours + ' '+hours1

            phone = loc['phone']
            latlng = loc['latlng']
            latitude = latlng.split(",")[0]
            longitude = latlng.split(",")[-1]

            
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if state_list:
                state = state_list[-1]
                
            store = []
            result_coords.append((latitude, longitude))
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city.strip() if city else '<MISSING>')
            store.append(state.strip() if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation.replace("Hours",' Hours ') if hours_of_operation.replace("Hours",' Hours ') else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            # print("====================",store)
            yield store
                  
        # print("==================================",current_results_len)
        if current_results_len < MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_zip()



def scrape():
    data  = fetch_data()
    write_output(data)

scrape()
