import csv
import requests
from bs4 import BeautifulSoup
import re
# import http.client
import sgzip
import json
# import  pprint
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
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

def fetch_data():
    base_url = "https://www.bylinebank.com"
    # conn = http.client.HTTPSConnection("guess.radius8.com")

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    coords = search.next_coord()
    current_results_len = 0
    # search.current_zip """"""""==zip
    header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
              "Content-Type":"application/x-www-form-urlencoded",
               "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
              }
    while coords:
        # try:
        result_coords = []
        url = 'https://bylinebank.locatorsearch.com/GetItems.aspx'
        # data = "lat=41.66097757926449&lng=-87.78996078404255&searchby=FCS%7CATMSF%7COFC%7C&SearchKey=&rnd=1569844320549"
        data = "lat="+str(coords[0])+"&lng="+str(coords[1])+"&searchby=FCS%7CATMSF%7COFC%7C&SearchKey=&rnd=1569844320549"
        # pagereq = request_wrapper(url,"post",data=data, headers=header)
        # if pagereq==None:
            # continue
        # print(coords)
        s = requests.Session()
        # r= requests.post(
        #     'https://bylinebank.locatorsearch.com/GetItems.aspx',
        #     headers=header,data=data,
        # )
        pagereq = s.get(url,data=data, headers=header)
        soup = BeautifulSoup(pagereq.content, 'html.parser')
        # for i in soup.find_all("marker"):
        #     print(i.attrs['lng'])
        add2 = soup.find_all("add2")
        address1 = soup.find_all("add1")
        current_results_len = len(address1)
        loc = soup.find_all("marker")
        hours = soup.find_all("contents")
        name = soup.find_all("title")
        locator_domain = "https://www.bylinebank.com"
        store_number ="<MISSING>"
        location_type ='bylinebank'
        for i in range(len(address1)):
            street_address = address1[i].text
            city = add2[i].text.split(",")[0]
            #print(add2[i].text)
            state = add2[i].text.replace(",,",",").split(",")[1].split( )[0]
            
            zip1 = add2[i].text.replace(",,",",").split(",")[1].split( )[1]
            if "<b>" in add2[i].text:
                phone = add2[i].text.split("<b>")[1].replace("</b>","").strip()
            else:
                phone = "<MISSING>"

            location_name = name[i].text.replace("<br>","")

            if len(zip1)==3 or len(zip1)==7:
                country_code = "CA"
            else:
                country_code = "US"
            soup_hour = BeautifulSoup(hours[i].text,'lxml')
            if soup_hour.find("table"):
                h = []
                for i in soup_hour.find("table"):
                    h.append(i.text)

                hour = "".join(h)
            else:
                hour = "<MISSING>"
            hours_of_operation = hour
            try:
                latitude = loc[i].attrs['lat']
                longitude = loc[i].attrs['lng']
            except:
                pass
            result_coords.append((latitude,longitude))
           
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip1 if zip1 else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type)
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append("https://www.bylinebank.com/locator/")
            if store[2] in addresses:
                continue
            addresses.append(store[2])

            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
      
        coords = search.next_coord()
        
        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
