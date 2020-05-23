import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url=  "https://www.orangetheory.com/bin/otf/studios?latitude=26.4029696&longitude=-80.1172975&distance=20000000" 
    r = session.get(base_url)   
    json_data = r.json()
    for j in json_data['data']:
        for i in j:
            base_url = "https://www.orangetheory.com/"
            hours_of_operation = "<MISSING>"
            store_number = i['studioId']
            street_address = i['studioLocation']['physicalAddress']
            if street_address == None:
                continue
            city  = i['studioLocation']['physicalCity']
            if city == "Ithaca":
                street_address = street_address.replace("\r\n","").split("Ithaca")[0]
            state  =  i['studioLocation']['physicalState']
            zipp  = i['studioLocation']['physicalPostalCode']
            if zipp == "20009":
                street_address = street_address.replace("\r\n","")
            if zipp == "29715":
                street_address = street_address.replace("\r\n","")
            latitude   = i['studioLocation']['latitude']
            if latitude == "1":
                latitude = "<MISSING>"
            longitude  = i['studioLocation']['longitude']
            if longitude == "1":
                longitude = "<MISSING>"
            location_name = i['studioName']
            country_code = i['studioLocation']['physicalCountry']
            phone = i['studioLocation']['phoneNumber']
            location_type ="Orangetheory Fitness"
            add = street_address.replace(" ","-").replace(".","").replace(",","").replace(" - ","-").replace("--","-").lower().replace("#","")
            add1 = city.lower().replace(" ","-").replace(".","").replace(",","").replace("#","")
            add2 = state.replace(" ","-").replace("QC","quebec").replace("BC","british-columbia").replace("MB","Manitoba").replace("AB","alberta").replace("NB","new-brunswick").replace("ON","ontario").replace("SK","saskatchewan").replace("YT","yukon").replace("NU","Nunavut").replace("QC","nova-scotia")
            if country_code == "Canada":
                page_url1 = "https://www.orangetheory.com/en-ca/locations/"+str(add2)+"/"+str(add1)+"/"+str(add)+"/"
            else:
                page_url1 = "https://www.orangetheory.com/en-us/locations/"+str(add2)+"/"+str(add1)+"/"+str(add)+"/"
            page_url = page_url1.replace("--","-")
            # print(page_url)
            # page_url=''
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if country_code == 'Mexico' or country_code == 'China'or country_code == 'Singapore'or country_code == 'Australia'or country_code == 'Guatemala'or country_code == 'Israel'or country_code == 'Poland'or country_code == 'Germany'or country_code == 'Spain'or country_code == 'India'or country_code == 'Hong Kong'or country_code == 'New Zealand'or country_code == 'United Arab Emirates'or country_code == 'Japan'or country_code == 'Chile'or country_code == 'United Kingdom' or country_code == 'Saudi Arabia'or country_code == '966551603333'or country_code == 'Kuwait'or country_code == 'Puerto Rico'or country_code == 'Peru'or country_code == 'Colombia'or country_code == 'Dominican Republic':
                continue
            if location_name == "Corporate Test Jose" or location_name == 'Test HR'or location_name == 'Perezidente'or location_name == 'Test OTbeat 006' or location_name == 'Test Nighthawk'or location_name == 'Test Nighthawk 2'or location_name == 'NPE'or location_name == 'Test 001'or location_name == 'Test 003'or location_name == 'VM009'or location_name == 'Test 004'or location_name == 'OTbeat MAV' or location_name == 'Test 005':
                continue
            if store[2] in address :
                continue
            address.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
