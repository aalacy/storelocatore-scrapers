import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
                r = requests.post(url,headers=headers,data=data)
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
    cords = sgzip.coords_for_radius(100)
    addresses = []
    r_headers = {
        'Accept': '*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,gu;q=0.8',
        'Content-Type': 'application/json; charset=UTF-8',    
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    for cord in cords:
        base_url = "https://sportclips.com"
        r_data = '{"strLocation":"1","strLat":' + str(cord[0]) + ',"strLng":' + str(cord[1]) + ',"strRadius":"100","country":"US"}'
        r = request_wrapper("https://sportclips.com/CustomWeb/StoreLocator.asmx/SearchByLocation", "post", headers=r_headers,data=r_data)
        if r == None:
            continue
        data = json.loads(r.json()["d"])["Results"]
        for i in data:
            page_url = i['Url']
            location_name = i['Title']
            if "COMING SOON!" in i['Address']:
                continue
            address_list = i['Address'].split('|')

            if ".com" in i['Url']:
                if len(address_list) == 5:
                    street_address = " ".join(address_list[:2]).replace("\t",'')
                    city = address_list[2].split(',')[0]
                    
                    zipp = address_list[2].split(',')[1].split(' ')[-1]
                
                elif len(address_list) == 3:
                    try:
                        street_address = address_list[0].replace("\t",'')
                        city = address_list[1].split(',')[0]
                        zipp = address_list[1].split(',')[1].split(' ')[-1]
                    except:
                        street_address = " ".join(address_list[:2]).replace("\t",'')
                        city = address_list[-1].split(',')[0]
                        zipp = address_list[-1].split(',')[1].split(' ')[-1]

                else:
                    street_address = address_list[0].replace("\t",'') 
                    try:
                        city = address_list[1].split(',')[0]               
                        zipp = address_list[1].split(',')[1].split(' ')[-1]
                    except:
                        city = address_list[2].split(',')[0]
                        zipp = address_list[2].split(',')[1].split(' ')[-1]
            else:
                if len(address_list) == 5:
                    street_address = " ".join(address_list[:2]).replace("\t",'')
                    city = address_list[2].split(',')[0]
                    
                    zipp = ' '.join(address_list[2].split(',')[1].split(' ')[-2:])
                
                elif len(address_list) == 3:
                    street_address = address_list[0].replace("\t",'')
                    city = address_list[1].split(',')[0]
                    zipp = ' '.join(address_list[1].split(',')[1].split(' ')[-2:])
                    
                else:
                    street_address = address_list[0].replace("\t",'') 
                    try:
                        city = address_list[1].split(',')[0]               
                        zipp = ' '.join(address_list[1].split(',')[1].split(' ')[-2:])
                    except:
                        city = address_list[2].split(',')[0]
                        zipp = ' '.join(address_list[2].split(',')[1].split(' ')[-2:])

            phone = address_list[-1].replace("Canal Winchester, Ohio 43110","<MISSING>")
            state = i['ExtCode'][:2]
            latitude = i['Lat']
            longitude = i['Long']
            location_type = "HairSalon"
            try:
                r1 = requests.get(page_url, headers=r_headers)
          
             
                soup1 = BeautifulSoup(r1.text, "lxml")
                
        
                if ".com" in i['Url']:
                    country_code = "US"
                    hours_of_operation = "".join(soup1.find("table").text.strip())
                    
                
                else:
                    country_code = "CA"
                    hours = ''
                    for i in range(0,7):
                        hours = hours+" "+soup1.find_all("div",{"class":"wtp-responsive-row row cols-25-75"})[i].text.strip()
                    hours_of_operation = hours
        
            except:
                hours_of_operation = "<MISSING>"
        
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
