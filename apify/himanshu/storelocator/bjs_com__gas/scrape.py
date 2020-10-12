
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import html
import os
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data(): 
    base_url = "https://www.bjs.com/gas"
    city_data = session.get("https://api.bjs.com/digital/live/apis/v1.0/clublocatorpage/statetowns/10201").json()
    for town in city_data['clubLocatorStateTownList']:
        for number in town['Towns']:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json'
            }
            town_number = number.split("|")[0]
            slug = number.split("|")[1].replace(" ","-").replace(",","").lower()
            url = "https://api.bjs.com/digital/live/api/v1.0/club/search/10201"
            payload = '{"Town":"'+str(town_number)+'","latitude":"","longitude":"","radius":"","zipCode":""}'
            json_data = session.post("https://api.bjs.com/digital/live/api/v1.0/club/search/10201",data=payload,headers=headers).json()
            for data in json_data['Stores']['PhysicalStore']:
                hours = ""
                for attr in data['Attribute']:
                    if attr['name'] == "Gas Hours":
                        hours = attr['displayValue'].replace("<br>"," ")
                if hours == "":
                    continue
                page_url = "https://www.bjs.com/cl/"+str(slug)+"/"+str(town_number)
                location_name = "BJ'S WHOLESALE CLUB AT" + data['Description'][0]['displayStoreName']
                street_address = " ".join(data['addressLine']).strip(".")
                city = data['city']
                state = data['stateOrProvinceName']
                zipp = data['postalCode']
                store_number = data['uniqueID']
                location_type = "GAS"
                phone = data['telephone1']
                lat = data['latitude']
                lng = data['longitude']
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)     
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()