import csv
import requests
from bs4 import BeautifulSoup
import re
import json
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
    base_url= "https://www.kohls.com/stores.shtml"
 
    r = requests.get(base_url)
   
    address =[]
    soup= BeautifulSoup(r.text,"lxml")
    a = (soup.find_all("a",{"class":"regionlist"}))
    # print()
    
    if a != []:
        for i in a :
            # print(i['href'])
            try:
                r1 = requests.get(i['href'])
            except:
                continue
            soup1 = BeautifulSoup(r1.text,"lxml")
            b =soup1.find_all("a",{"class":"citylist"})
            if b != []:
                for j in b :
                    # print(j['href'])
                    try:
                        r2 = requests.get(j['href'])
                    except:
                        continue
                    soup2 = BeautifulSoup(r2.text,"lxml")
                    c =soup2.find("span",{"class":"location-title"})
                    if c != [] and c != None:
                        for k in c:
                            try:
                                r3 = requests.get(k['href'])
                            except:
                                continue
                            soup3 = BeautifulSoup(r3.text,"lxml")
                            d = soup3.find("script",{"type":"application/ld+json"})
                            json_data = json.loads(re.sub(r"\s+", " ",d.text.strip().lstrip()))
                            if type(json_data)==list: 
                                for l in json_data:
                                    location_name = l['name']
                                    latitude = l['geo']['latitude']
                                    longitude = l['geo']['longitude']
                                    hours_of_operation = l['openingHours']
                                    phone = l['address']['telephone']
                                    street_address = l['address']['streetAddress']
                                    city = l['address']['addressLocality']
                                    state = l['address']['addressRegion']
                                    zip1 = l['address']['postalCode']
                                    # print(hours_of_operation)
                            else:
                                location_name = json_data['name']
                                latitude =json_data['geo']['latitude']
                                longitude = json_data['geo']['longitude']
                                hours_of_operation = json_data['openingHours']
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
                                store.append("<MISSING>")
                                store.append(phone)
                                store.append("<MISSING>")
                                store.append(latitude)
                                store.append(longitude)
                                store.append(hours_of_operation)
                                store.append(k['href']) 
                                #print("--------------------",store)
                                if store[2] in address :
                                    continue
                                address.append(store[2])
                                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
