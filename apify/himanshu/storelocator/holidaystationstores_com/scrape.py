import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code","store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }   
    base_url = "https://www.holidaystationstores.com/Locations/Search"
    r = requests.post(base_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = soup.find("script",{"type":"text/javascript"}).text.split('=')[1].replace('};','}')
    data1 = json.loads(re.sub("(\w+):", r'"\1":',data))
    for i in data1:
        store_number = data1[i]['ID']
        latitude = data1[i]['Lat']
        longitude = data1[i]['Lng']

        location_url = "https://www.holidaystationstores.com/Locations/store/" +str(store_number) + "?page=0"
        
        is_true = True
        while is_true:
            r1 = requests.post(location_url,"lxml")
            soup1 = BeautifulSoup(r1.text, "lxml")
            info = soup1.find("div",{"id":"StoreDetails"})
            if info != None:
                is_true = False
            else:
                continue
        t = list(info.stripped_strings)
        # print(t)
        if t[6] == "24 hours, 7 days a week":
            street_address = t[1]
            city = t[2].split(',')[0]
            state = t[2].split(',')[1]
            zip1 = t[2].split(',')[2]
            phone = t[4]
            hours_of_operation = t[6]
            location_name = "Store #"+data1[i]['Name']+"-"+city+","+state
        elif t[5] == "24 hours, 7 days a week":
            street_address = t[1]
            city = t[2].split(',')[0]
            state = t[2].split(',')[1]
            zip1 = t[2].split(',')[2]
            phone = "<MISSING>"
            hours_of_operation = t[5]
            location_name = "Store #"+data1[i]['Name']+"-"+city+","+state
        else:
            street_address = t[1]
            city = t[2].split(',')[0]
            state = t[2].split(',')[1]
            zip1 = t[2].split(',')[2]
            phone = t[4]
            hours_of_operation = ''.join(t[6:20])
            location_name = "Store #"+data1[i]['Name']+"-"+city+","+state
        store = []
        address =[]
        store.append("www.holidaystationstores.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip1)   
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude )
        store.append(longitude )
        store.append(hours_of_operation)
        store.append(location_url)
        if store[2] in address:
            continue     
        address.append(store[2])
        yield store

    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
