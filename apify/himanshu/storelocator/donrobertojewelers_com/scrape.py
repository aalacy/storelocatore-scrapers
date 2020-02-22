import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.donrobertojewelers.com"
    locations_url = "/ustorelocator/location/map/?page="
    header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': "www.donrobertojewelers.com",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    body = "ajax=1"
    return_main_object = []
    page_id = 0
    location_id = 0
    cleanr = re.compile('<.*?>')
    while True:
        page_id = page_id + 1
        # print(page_id)
        page_reqeust = requests.post(base_url+locations_url+str(page_id),headers=header,data=body)
        locations = page_reqeust.json()["markers"]
        if locations[0]['location_id'] == location_id:
            break
        else:
            location_id = locations[0]['location_id']
            for i in range(len(locations)):
                store_data = locations[i]
                store=[]
                # store.append("https://www.donrobertojewelers.com")
                location_name = (store_data['title'])
                if store_data["address_zip"] == None or store_data["address_zip"] == "":
                    if len(store_data["address"].split(".")) == 3:
                        street_address = (store_data["address"].split(".")[0])
                        city = (store_data['address'].split(".")[1].split(" ")[1])
                    else:
                        street_address = (" ".join(store_data["address"].split(" ")[0:-4]).replace("                           ","").replace("  Victorville CA 92392",""))
                        city = (" ".join(store_data['address'].split(" ")[-4:-2]).replace('125 Hemet,',"Hemet").replace("64, Northridge,",'Northridge'))   
                    state =  (store_data["address"].split(" ")[-2])
                    zipp = (store_data['address'].split(" ")[-1])        
                else:
                    street_address = (store_data["address_street"])
                    city = (store_data['address_city'])
                    state = (store_data['address_state'])
                    zipp = (store_data["address_zip"])
                country_code = ("US") 
                store_number = (store_data["location_id"])
                phone = (store_data['phone'])
                location_type = ("<MISSING>")
                latitude = (store_data["latitude"])
                longitude = (store_data["longitude"])    
                if re.sub(cleanr, '', store_data["hours"]) == "":
                    hours_of_operation = ("<MISSING>")
                else:
                    hours_of_operation = (re.sub(cleanr, '', store_data["hours"].replace("\n","").replace("\t","").replace("\r","").strip().rstrip().lstrip()))
                page_url = (("<MISSING>"))
                if "Victorville" in store_data['title']:
                    zipp = (" ".join(store_data["address"].split(" ")[0:-4]).split(" ")[9])
                    city = (" ".join(store_data["address"].split(" ")[0:-4]).split(" ")[7])
                    state = (" ".join(store_data["address"].split(" ")[0:-4]).split(" ")[8])
                    street_address = (" ".join(" ".join(store_data["address"].split(" ")[0:-4]).split(" ")[0:6]))
                if "Hemet" in location_name:
                    street_address = street_address + " " + "125"
                if "Northridge" in location_name:
                    street_address = street_address + " " + "64"
                store = []
                store.append("https://www.donrobertojewelers.com")
                store.append(location_name if location_name else "<MISSING>" )
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")   
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else"<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type if location_type else"<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>" )  
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
