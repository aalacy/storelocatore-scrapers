import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 25
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    }

    base_url = "https://www.seattlesbest.com"

    while zip_code:
        result_coords = []

        # print("zip_code === "+zip_code)
        locator_domain = "https://www.seniorhelpers.com/"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        location_url = "https://portal.seniorhelpers.com/api/offices"
        data="------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"zip\"\r\n\r\n"+str(zip_code)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" 
        
        try:
            r = requests.post(location_url,headers=headers,data=data)
        except:
            pass
        soup = BeautifulSoup(r.text, "html5lib")
        current_results_len = len(soup.find_all("marker"))    
        for data in soup.find_all("marker"):
            city = str(data.find("city")).replace("<city><!--[CDATA[",'').replace("]]--></city>",'')
            state = str(data.find("state")).replace("<state><!--[CDATA[",'').replace("]]--></state>",'')
            zipp = str(data.find("zip")).replace("<zip><!--[CDATA[",'').replace("]]--></zip>",'')
            phone = str(data.find("phone")).replace("<phone><!--[CDATA[",'').replace("]]--></phone>",'')
            latitude = str(data.find("lat")).replace("<lat><!--[CDATA[",'').replace("]]--></lat>",'')
            longitude = str(data.find("lng")).replace("<lng><!--[CDATA[",'').replace("]]--></lng>",'')
            
            street_address = str(data.find("address")).replace("<address><!--[CDATA[",'').replace("]]--></address>",'')
            location_name = str(data.find("name")).replace("<name><!--[CDATA[",'').replace("]]--></name>",'')

            # print(address,lng)

            soup1 = BeautifulSoup(str(data.find("alias")).replace("<!--","").replace("-->",""), "html5lib")
            page_url="https://www.seniorhelpers.com/"+soup1.text.replace("[CDATA[","").replace("]]",'')
            try:
                r1 = requests.get(page_url,headers=headers)
                soup2 = BeautifulSoup(r1.text, "html5lib")
            except:
                pass
            try:
                hours_of_operation = " ".join(list(soup2.find("i",{"class":"fas fa-clock"}).parent.stripped_strings)).replace("Hours ",'')
            except:
                hours_of_operation="<MISSING>"
                # it always need to set total len of record.



            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address.encode('ascii', 'ignore').decode('ascii').strip(), city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            print("data = " + str(store))
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            yield store
            # return_main_object.append(store)

        # yield store
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
