import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    adressess = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }

    base_url = "https://www.benspretzels.com/"
    json_url = "https://app.locatedmap.com/initwidget/?instanceId=b8d5e841-7e84-4b86-af79-9341996bc5ef&compId=comp-izqi4x5u&viewMode=json&styleId=style-jr7yn9r0"
    r = session.get(json_url,headers=headers)
    json_data = json.loads(r.json()['mapSettings'])[0]['fields']['unpublishedLocations']
   
   
    for dt in json_data:
        location_name = dt['name']
        temp_add = dt['formatted_address'].split(",")
        
        if len(temp_add) == 2:
            temp_st = temp_add[0].split(" ")
            street_address = " ".join(temp_st[:-1])
            city = temp_st[-1]
            state = temp_add[1].split(" ")[-2]
            zipp = temp_add[1].split(" ")[-1]
        else:
            street_address = temp_add[0].strip()
            city = temp_add[1].strip()
            state_zip = temp_add[2].split(" ") 
            if len(state_zip) == 2:
                state = state_zip[-1]
                zipp = temp_add[-1]
            else:
                state = state_zip[-2]
                zipp = state_zip[-1]

            phone = dt['tel']
            location_type = "<MISSING>"
            latitude = dt['latitude']
            longitude = dt['longitude']

            if dt['opening_hours'] == "":
                hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = dt['opening_hours'].replace("Ben's Soft Pretzels is located inside Spartan Stadium at Michigan State University","<MISSING>").replace("Ben's Soft Pretzels at Ohio Stadium at The Ohio State University","<MISSING>")
        
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
        store.append(hours_of_operation)
        store.append("<MISSING>")
        if store[2] in adressess:
            continue
        adressess.append(store[2])
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

