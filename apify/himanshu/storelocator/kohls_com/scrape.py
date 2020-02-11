import csv
import requests
from bs4 import BeautifulSoup
import re
import json
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # with open('ListingsPull-Amsterdam.csv', mode='a') as fd:
        #     writer = csv.writer(fd)
        #     rest_array = [text.encode("utf8") for text in rest_array]
        #     writer.writerow(rest_array)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    base_url= "https://www.kohls.com/stores.shtml"
    r = requests.get(base_url)
    address =[]
    soup= BeautifulSoup(r.text,"lxml")
    a = (soup.find_all("a",{"class":"regionlist"}))
    for i in a :
        r1 = requests.get(i['href'])
        soup1 = BeautifulSoup(r1.text,"lxml")
        b =soup1.find_all("a",{"class":"citylist"})
        for j in b :
            try:
                r2 = requests.get(j['href'])
            except:
                pass
            soup2 = BeautifulSoup(r2.text,"lxml")
            c =soup2.find_all("span",{"class":"location-title"})
            if c != [] and c != None:
                for k in c:
                    y = (k.find("a")['href'])
                    # print(y)
                    store_number = y.split("-")[1].split(".s")[0]
                    # print(store_number)
                    try:
                        r3 = requests.get(y,headers=headers)
                    except:
                        continue
                    soup3 = BeautifulSoup(r3.text,"lxml")
                    d = soup3.find("script",{"type":"application/ld+json"})
                    json_data = json.loads(re.sub(r"\s+", " ",d.text.strip().lstrip()))
                    # print(json_data)
                    if type(json_data)==list: 
                        for l in json_data:
                            location_name = l['name']
                            latitude = l['geo']['latitude']
                            longitude = l['geo']['longitude']
                            hours_of_operation = l['openingHours'].replace("24:00","12:00").replace("23:00","11:00").replace("22:00","10:00") \
                            .replace("21:00","9:00").replace("20:00","8:00").replace("19:00","7:00").replace("18:00","6:00").replace("17:00","5:00") \
                            .replace("16:00","4:00").replace("13:00","1:00").replace("14:00","2:00").replace("15:00","3:00") \
                            .replace("Su","Sun").replace("Mo","Mon").replace("Tu","Tue").replace("We","Wed").replace("Th","Thu").replace("Fr","Fri" ).replace("Sa","Sat")
                            phone = l['address']['telephone']
                            street_address = l['address']['streetAddress']
                            city = l['address']['addressLocality']
                            state = l['address']['addressRegion']
                            zip1 = l['address']['postalCode']       
                    else:
                        location_name = json_data['name']
                        latitude =json_data['geo']['latitude']
                        longitude = json_data['geo']['longitude']
                        hours_of_operation = json_data['openingHours'].replace("24:00","12:00").replace("23:00","11:00").replace("22:00","10:00").replace("21:00","9:00")\
                        .replace("20:00","8:00").replace("19:00","7:00").replace("18:00","6:00").replace("17:00","5:00").replace("16:00","4:00").replace("13:00","1:00") \
                        .replace("14:00","2:00").replace("15:00","3:00") \
                        .replace("Su","Sun").replace("Mo","Mon").replace("Tu","Tue").replace("We","Wed").replace("Th","Thu").replace("Fr","Fri" ).replace("Sa","Sat")
                        phone = json_data['address']['telephone']
                        street_address = json_data['address']['streetAddress']
                        city = json_data['address']['addressLocality']
                        state = json_data['address']['addressRegion']
                        zip1 = json_data['address']['postalCode']
                    store = []
                    store.append("https://www.kohls.com/")
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zip1)   
                    store.append("US")
                    store.append( store_number if store_number else"<MISSING>")
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)
                    store.append(y) 
                    # print("--------------------",store)
                    if store[2] in address :
                        continue
                    address.append(store[2])
                    yield store
    r2 = requests.get("https://www.kohls.com/stores/wy/casper-1420.shtml")
    address =[]
    soup2 = BeautifulSoup(r2.text,"lxml")
    d2 = soup2.find("script",{"type":"application/ld+json"})
    json_data2 = json.loads(re.sub(r"\s+", " ",d2.text.strip().lstrip()))
    if type(json_data2)==list: 
        for l2 in json_data2:
            # print(l)
            location_name2 = l2['name']
            latitude2 = l2['geo']['latitude']
            longitude2 = l2['geo']['longitude']
            hours_of_operation2 = l2['openingHours'].replace("24:00","12:00").replace("23:00","11:00").replace("22:00","10:00") \
            .replace("21:00","9:00").replace("20:00","8:00").replace("19:00","7:00").replace("18:00","6:00").replace("17:00","5:00") \
            .replace("16:00","4:00").replace("13:00","1:00").replace("14:00","2:00").replace("15:00","3:00") \
            .replace("Su","Sun").replace("Mo","Mon").replace("Tu","Tue").replace("We","Wed").replace("Th","Thu").replace("Fr","Fri" ).replace("Sa","Sat")
            phone2 = l2['address']['telephone']
            street_address2 = l2['address']['streetAddress']
            city2 = l2['address']['addressLocality']
            state2 = l2['address']['addressRegion']
            zip3 = l2['address']['postalCode']
            store_number2 = y.split("-")[1].split(".s")[0]
            # print(l)
            store2 = []
            store2.append("https://www.kohls.com/")
            store2.append(location_name2)
            store2.append(street_address2)
            store2.append(city2)
            store2.append(state2)
            store2.append(zip3)   
            store2.append("US")
            store2.append(store_number2 if store_number2 else"<MISSING>")
            store2.append(phone2)
            store2.append("<MISSING>")
            store2.append(latitude2)
            store2.append(longitude2)
            store2.append(hours_of_operation2)
            store2.append("https://www.kohls.com/stores/wy/casper-1420.shtml") 
            # print("--------------------",store2)
            if store2[2] in address:
                continue
            address.append(store2[2])
            yield store2
    r1 = requests.get("https://www.kohls.com/stores/wy/cheyenne-1205.shtml")
    address =[]
    soup1 = BeautifulSoup(r1.text,"lxml")
    d1 = soup1.find("script",{"type":"application/ld+json"})
    json_data1 = json.loads(re.sub(r"\s+", " ",d1.text.strip().lstrip()))
    if type(json_data1)==list: 
        for l1 in json_data1:
            # print(l)
            location_name1 = l1['name']
            latitude1 = l1['geo']['latitude']
            longitude1 = l1['geo']['longitude']
            hours_of_operation1 = l1['openingHours'].replace("24:00","12:00").replace("23:00","11:00").replace("22:00","10:00") \
            .replace("21:00","9:00").replace("20:00","8:00").replace("19:00","7:00").replace("18:00","6:00").replace("17:00","5:00") \
            .replace("16:00","4:00").replace("13:00","1:00").replace("14:00","2:00").replace("15:00","3:00") \
            .replace("Su","Sun").replace("Mo","Mon").replace("Tu","Tue").replace("We","Wed").replace("Th","Thu").replace("Fr","Fri" ).replace("Sa","Sat")
            phone1 = l1['address']['telephone']
            street_address1 = l1['address']['streetAddress']
            city1 = l1['address']['addressLocality']
            state1 = l1['address']['addressRegion']
            zip2 = l1['address']['postalCode']
            store_number1 = y.split("-")[1].split(".s")[0]
            # print(l)
            store1 = []
            store1.append("https://www.kohls.com/")
            store1.append(location_name1)
            store1.append(street_address1)
            store1.append(city1)
            store1.append(state1)
            store1.append(zip2)   
            store1.append("US")
            store1.append(store_number1 if store_number1 else"<MISSING>")
            store1.append(phone1)
            store1.append("<MISSING>")
            store1.append(latitude1)
            store1.append(longitude1)
            store1.append(hours_of_operation1)
            store1.append("https://www.kohls.com/stores/wy/cheyenne-1205.shtml") 
            # print("--------------------",store1)
            if store1[2] in address:
                continue
            address.append(store1[2])
            yield store1
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
