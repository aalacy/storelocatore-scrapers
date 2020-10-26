
import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    # search.initialize()
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 100
    MAX_DISTANCE = 25
    current_results_len = 0 
    main_arr=[]
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while coord:
        result_coords = []
        lat = str(coord[0])
        lng = str(coord[1])
        print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #print('Pulling Lat-Long %s,%s..' % (lat,lng))
        # print(lng)
        base_url="https://www.pizza73.com/Pizza73/proxy.php?lng="+str(lng)+"&lat="+str(lat)
        try:
            r = requests.get(base_url)
            json_data = r.json()
        except:
            pass
        current_results_len =len(json_data['data'])
        for i in json_data['data']:
                b = i['OPERATING_HOUR_SET']
                soup= BeautifulSoup(b,"lxml")
                hours_of_operation = (soup.text.replace('AM','AM ').replace(","," , ").replace("PM","PM "))
                street_address = i["streetNumber"]+' '+i["ADDRESS_LINE_1"]
                city = i["CITY"]
                state = i["PROVINCE"]
                zipp = i["POSTAL_CODE"]
                phone = i["STORE_PHONE_NO"]
                latitude = i["storeLatitude"]
                longitude = i["storeLongitude"]
                store_number = i["STORE_ID"]
                store = []
                store.append("https://www.pizza73.com/Pizza73/")
                store.append("<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("CA")
                store.append(store_number if store_number else "<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation.replace(" , ",' '))
                # print(store)
                store.append(base_url)
                main_arr.append(store)
                # if store[2] in addresses:
                #     continue
                # addresses.append(store[2])
                #print("data ==="+str(store))
                #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                # yield store
                 
       
        if current_results_len < MAX_RESULTS:
            
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


    base_url2='https://www.pizza73.com/Pizza73/proxy.php?lng=-115.6654225&lat=54.1273952'
    
    try:
        r1 = requests.get(base_url2)
    except:
        pass
    json_data = r1.json()
    current_results_len =len(json_data['data'])

    for i in json_data['data']:
        b = i['OPERATING_HOUR_SET']
        soup= BeautifulSoup(b,"lxml")
        hours_of_operation = (soup.text.replace('AM','AM ').replace(","," , ").replace("PM","PM "))
        street_address = i["streetNumber"]+' '+i["ADDRESS_LINE_1"]
        city = i["CITY"]
        state = i["PROVINCE"]
        zipp = i["POSTAL_CODE"]
        phone = i["STORE_PHONE_NO"]
        latitude = i["storeLatitude"]
        longitude = i["storeLongitude"]
        store_number = i["STORE_ID"]
        store = []
        store.append("https://www.pizza73.com/Pizza73/")
        store.append("<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("CA")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation.replace(",",' '))
        store.append(base_url2)
        main_arr.append(store)
        # print(store)
        # if store[2] in addresses:
        #     continue
        # addresses.append(store[2])
        #print("data ==="+str(store))
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

    base_url1='https://www.pizza73.com/Pizza73/proxy.php?lng=-113.9577884&lat=51.15473189999999'
    
    try:
        r1 = requests.get(base_url1)
    except:
        pass
    json_data = r1.json()
    current_results_len =len(json_data['data'])

    for i in json_data['data']:
        b = i['OPERATING_HOUR_SET']
        soup= BeautifulSoup(b,"lxml")
        hours_of_operation = (soup.text.replace('AM','AM ').replace(","," , ").replace("PM","PM "))

        street_address = i["streetNumber"]+' '+i["ADDRESS_LINE_1"]
        city = i["CITY"]
        state = i["PROVINCE"]
        zipp = i["POSTAL_CODE"]
        phone = i["STORE_PHONE_NO"]
        latitude = i["storeLatitude"]
        longitude = i["storeLongitude"]
        store_number = i["STORE_ID"]
        store = []
        store.append("https://www.pizza73.com/Pizza73/")
        store.append("<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("CA")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation.replace(",",' '))
        store.append(base_url)
        main_arr.append(store)
        # print(store)
        # if store[2] in addresses:
        #     continue
        # addresses.append(store[2])
        #print("data ==="+str(store))
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        # yield store
    for data in range(len(main_arr)):
        if main_arr[data][2] in addresses:
            continue
        addresses.append(main_arr[data][2])
        yield main_arr[data]
                  
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
