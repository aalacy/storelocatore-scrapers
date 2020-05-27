import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
import requests
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
    r = requests.get(base_url)   
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
            add = street_address.replace(" ","-").replace(".","").replace(",","").replace(" - ","-").replace("--","-").lower().replace("#","").replace("&","")
            add1 = city.lower().replace(" ","-").replace(".","").replace(",","").replace("#","").replace("&","").replace("--","-")
            add2 = state.replace(" ","-").replace("QC","quebec").replace("BC","british-columbia").replace("MB","Manitoba").replace("AB","alberta").replace("NB","new-brunswick").replace("ON","ontario").replace("SK","saskatchewan").replace("YT","yukon").replace("NU","Nunavut").replace("QC","nova-scotia")
            if country_code == "Canada":
                page_url1 = "https://www.orangetheory.com/en-ca/locations/"+str(add2)+"/"+str(add1)+"/"+str(add)+"/"
            else:
                page_url1 = "https://www.orangetheory.com/en-us/locations/"+str(add2)+"/"+str(add1)+"/"+str(add)+"/"
            page_url = page_url1.replace("--","-")
            if zipp == "N1R 7N7":
                page_url = page_url.replace("road","rd") 
            if zipp =='32771':
                page_url = page_url.replace("/&","").replace("&","").replace(";","-")
            if zipp =='V7P 1S8':
                page_url = page_url.replace("107-1171-marine-drive","1171-marine-drive-107")
            if zipp =='V3W 2M1':
                page_url = page_url.replace("12101-72","1210172").replace("ontario","british-columbia")
            if zipp =='V6K 2G9':
                page_url = page_url.replace("3055","3097").replace("broadway","broadwayrnvancouver-bc-v6k-2g9")
            if zipp == "L6J 7S8":
                page_url = page_url.replace("oakville","toronto")
            if zipp == "V3H 0E6":
                page_url = page_url.replace("unit-","")
            if zipp == "V9B 5E3":
                page_url = page_url.replace("victoria/2945-jacklin-road-unit-133/","langford/unit-133-2956-jacklin-road/")
            if zipp == "T8V 4E9":
                page_url = page_url.replace("grande-prairie/102-11510-westgate-drive/","grand-prairie/unit-102-11510-westgate-dr/")
            if zipp == "V3W 2M1" or zipp == "R3K 2G6":
                page_url = page_url.replace("avenue","ave")
            if zipp == "V4A 2H9":
                page_url = page_url.replace("surrey/540-15355-24th-avenue/","richmond-hill/15355-24th-avenue-unit-540/")
            if zipp == "V2T 0B5":
                page_url = page_url.replace("abbotsford/110-2653-tretheway-st/","vancouver/110-2653-tretheway-street/") 
            if zipp == "32803":
                page_url = page_url.replace("-dr-","-dr")
            if zipp == "33431":
                page_url = page_url.replace("-nw-","-n-w-")
            if zipp == "J6A 8J4":
                page_url = page_url.replace("lafayettee","lafayette")
            if zipp == "J7V 0H1":
                page_url = page_url.replace("saint","ste")
            if zipp == "T9K 2Z7":
                page_url = page_url.replace("fort","ft")
            if zipp == "T7X 4B8":
                page_url = page_url.replace("118-7-mcleod-avenue","7-mcleod-avenue-118")
            if zipp == "T8N 5C9":
                page_url = page_url.replace("stalbert","st-albert")
            if zipp == "T5Z 3L2":
                page_url = page_url.replace("16620-95-street-nw-","16640-95-street")
            if zipp == "T5T 4K3":
                page_url = page_url.replace("edmonton","callingwood")
            if zipp == "T5T 4K3":
                page_url = page_url.replace("edmonton","callingwood")
            if zipp == "R2E 0H9":
                page_url = page_url.replace("east-st-paul/7-","winnipeg/7")
            if zipp == "B4B 0S9":
                page_url = page_url.replace("NS","nova-scotia").replace("blvd-unit","blvdrnunit")
            if zipp == "L4J 8W1":
                page_url = page_url.replace("-st-","-street-")
            if zipp == "46220":
                page_url = page_url.replace("IN","indiana").replace("5858-north-college-avenue","2727-e-86th-street-suite-115")
            if zipp == "N2T 2W1":
                page_url = page_url.replace("west","w")
            if zipp == "L9T 6R1":
                page_url = page_url.replace("unit-e1-1250-steeles-ave-e","1250-steeles-ave-e-unit-e1")   
            store = []
            store.append(base_url if base_url.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
            store.append(location_name if location_name.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>") 
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
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if country_code == 'Mexico' or country_code == 'China'or country_code == 'Singapore'or country_code == 'Australia'or country_code == 'Guatemala'or country_code == 'Israel'or country_code == 'Poland'or country_code == 'Germany'or country_code == 'Spain'or country_code == 'India'or country_code == 'Hong Kong'or country_code == 'New Zealand'or country_code == 'United Arab Emirates'or country_code == 'Japan'or country_code == 'Chile'or country_code == 'United Kingdom' or country_code == 'Saudi Arabia'or country_code == '966551603333'or country_code == 'Kuwait'or country_code == 'Puerto Rico'or country_code == 'Peru'or country_code == 'Colombia'or country_code == 'Dominican Republic'or country_code == "Costa Rica":
                continue
            if location_name == "Corporate Test Jose" or location_name == 'Test HR'or location_name == 'Perezidente'or location_name == 'Test OTbeat 006' or location_name == 'Test Nighthawk'or location_name == 'Test Nighthawk 2'or location_name == 'NPE'or location_name == 'Test 001'or location_name == 'Test 003'or location_name == 'VM009'or location_name == 'Test 004'or location_name == 'OTbeat MAV' or location_name == 'Test 005'or location_name == 'Barrhaven':
                continue
            if zipp == "V2N 2S9" or zipp == "K2J 6K8" :
                continue
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
