import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
session = SgRequests()
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
    address = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    base_url = "https://www.rosesdiscountstores.com/superdollar"
    link = "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=51.705851%2C-30.854462&southwest=1.599136%2C-119.92419"
    json_data = requests.get(link, headers=headers).json()['locations']
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = "https://www.rosesdiscountstores.com/store-locator-index"
    for data in json_data:
        location_name = data['name']
        location_type = data['name']
        addr = data['address'].split(",")
        if " US" == addr[-1]:
            del addr[-1]
        if "United States" in addr[-1]:
            del addr[-1]
        if data['address1']:
            street_address = (data['address1']+ " " + str(data['address2'])).strip()
        else:
            street_address = " ".join(addr[:-2]).strip()
        if data['city']:

            city = data['city']
        else:
            city = addr[1].strip()
        state = data['region']
        if data['postcode']:
            zipp = data['postcode']
        else:
            try:
                zipp = re.findall(r'\b[0-9]{5}(?:-[0-9]{4})?\b',data['address'])[-1].strip()
            except:
                zipp = "<MISSING>"
        if "con_wg5rd22k" in data['contacts']:
            phone = data['contacts']['con_wg5rd22k']['text']
        else:
            phone = "<MISSING>"
        latitude = data['lat']
        longitude = data['lng']
        if "hoursOfOperation" in data['hours'] :
            hours1 = data['hours']['hoursOfOperation']
            hours2 = "Monday"+" : "+hours1['mon']+", "+"Tueday"+" : "+hours1['tue']+", "+"Wednesday"+" : "+hours1['wed']+", "+"Thurseday"+" : "+hours1['thu']+", "+"Friday"+" : "+hours1['fri']+", "+"Saturday"+" : "+hours1['sat']+", "+"Sunday"+" : "+hours1['sun']
            hours_of_operation = hours2.replace("20","08").replace("21","09").replace("22","10").replace("19","07").replace("18","06").replace(":00-"," AM - ").replace(":00"," PM")
        elif data["hours"] == "hrs_a4db656x":
            hours_of_operation = "Monday : 09 AM - 06 PM, Tueday : 09 AM - 06 PM, Wednesday : 09 AM - 06 PM, Thurseday : 09 AM - 06 PM, Friday : 09 AM - 06 PM, Saturday : 09 AM - 06 PM, Sunday : 12 AM - 06 PM"
        elif data["hours"] == "hrs_ywfef43p":
            hours_of_operation = "Monday : 09 AM - 09 PM, Tueday : 09 AM - 09 PM, Wednesday : 09 AM - 09 PM, Thurseday : 09 AM - 09 PM, Friday : 09 AM - 09 PM, Saturday : 09 AM - 09 PM, Sunday : 10 AM - 08 PM"
        else:
            hours_of_operation = "<MISSING>"
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
        if store[2] in address :
           continue
        address.append(store[2])
        yield store


    base_url = "https://www.rosesdiscountstores.com/superdollar"
    link = "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?countryCode=US&name=Bargain%20Town&query=Bargain%20Town&radius=80467"
    json_data = requests.get(link, headers=headers).json()['locations']
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = "https://www.rosesdiscountstores.com/store-locator-index"
    for data in json_data:
        location_name = data['name']
        location_type = data['name']
        addr = data['address'].split(",")
        if " US" == addr[-1]:
            del addr[-1]
        if "United States" in addr[-1]:
            del addr[-1]
        if data['address1']:
            street_address = (data['address1']+ " " + str(data['address2'])).strip()
        else:
            street_address = " ".join(addr[:-2]).strip()
        if data['city']:

            city = data['city']
        else:
            city = addr[1].strip()
        state = data['region']
        if data['postcode']:
            zipp = data['postcode']
        else:
            try:
                zipp = re.findall(r'\b[0-9]{5}(?:-[0-9]{4})?\b',data['address'])[-1].strip()
            except:
                zipp = "<MISSING>"
        if "con_wg5rd22k" in data['contacts']:
            phone = data['contacts']['con_wg5rd22k']['text']
        else:
            phone = "<MISSING>"
        latitude = data['lat']
        longitude = data['lng']
        if "hoursOfOperation" in data['hours'] :
            hours1 = data['hours']['hoursOfOperation']
            hours2 = "Monday"+" : "+hours1['mon']+", "+"Tueday"+" : "+hours1['tue']+", "+"Wednesday"+" : "+hours1['wed']+", "+"Thurseday"+" : "+hours1['thu']+", "+"Friday"+" : "+hours1['fri']+", "+"Saturday"+" : "+hours1['sat']+", "+"Sunday"+" : "+hours1['sun']
            hours_of_operation = hours2.replace("20","08").replace("21","09").replace("22","10").replace("19","07").replace("18","06").replace(":00-"," AM - ").replace(":00"," PM")
        elif data["hours"] == "hrs_a4db656x":
            hours_of_operation = "Monday : 09 AM - 06 PM, Tueday : 09 AM - 06 PM, Wednesday : 09 AM - 06 PM, Thurseday : 09 AM - 06 PM, Friday : 09 AM - 06 PM, Saturday : 09 AM - 06 PM, Sunday : 12 AM - 06 PM"
        elif data["hours"] == "hrs_ywfef43p":
            hours_of_operation = "Monday : 09 AM - 09 PM, Tueday : 09 AM - 09 PM, Wednesday : 09 AM - 09 PM, Thurseday : 09 AM - 09 PM, Friday : 09 AM - 09 PM, Saturday : 09 AM - 09 PM, Sunday : 10 AM - 08 PM"
        else:
            hours_of_operation = "<MISSING>"
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
        if store[2] in address :
           continue
        address.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
