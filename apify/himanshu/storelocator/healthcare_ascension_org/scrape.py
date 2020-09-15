import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = "https://healthcare.ascension.org"
    for loc_type in ["Emergency Care","Express Care","Hospital/Medical Center","Imaging","Laboratory","Other","Pharmacy","Primary Care/Clinic","Specialty Care","Urgent Care"]:
        payload = "{\r\n    \"geoDistanceOptions\":\r\n    {\r\n        \"location\":\"Phoenix, AZ  85029\",\r\n        \"radius\":\"6000\"\r\n    },\r\n    \"facilityName\":\"\",\r\n    \"locationType\":\""+str(loc_type)+"\",\r\n    \"page\":1,\r\n    \"pageSize\":60000,\r\n    \"stateCode\":\"\",\r\n    \"filters\":\r\n    {\r\n        \"locationType\":[\""+str(loc_type)+"\"]\r\n        }\r\n}"
        headers = {
            'accept': '*/*',
            'content-type': 'application/json; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        json_data = session.post("https://healthcare.ascension.org/api/locations/search",headers=headers,data=payload).json()
        
        for data in json_data['Results']:

            info = data['Data']['Location']
            
            location_name = info['DisplayName']
            street_address = info['Address']['Street']
            if info['Address']['Street2']:
                street_address += " " + info['Address']['Street2']
            city = info['Address']['City']
            state = info['Address']['State']
            zipp = info['Address']['Zip']
            phone = info['PhoneNumber']
            location_type = loc_type
            page_url = base_url+info['Url'].replace(" ","%20")
            latitude = info['Address']['Latitude']
            longitude = info['Address']['Longitude']
            hours = re.sub(r'\s+'," ",info['Hours']).replace("Call us for daily hours.",'').replace("Call us for daily hours",'').replace("Visiting Hours:",'').replace("Emergency Dept: ",'').replace("Basani: ",'').replace("Business Office Hours:",'').replace("Hours Vary By Office",'').replace(" (Call for Holiday Hours)",'').replace("Varies","").replace("Contact us for hours. ",'').replace("Clinic & Same Day Appointments: ",'').replace("Contact us for daily hours.",'').replace("Appointments: First, third and fifth Thursday of every month.",'').replace("Family Medicine: ",'').lstrip().replace(" Lab: by appointment only","").replace("Urgent Care: 920-223-7305",'').replace("24/7","Open 24/7")

            if hours.strip():
                hours=hours
            else:
                hours = "<MISSING>"


            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if str(store[2]+str(phone)+store[-1]) in addresses:
                continue
            addresses.append( str(store[2]+str(phone) +store[-1])) 
            yield store
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
