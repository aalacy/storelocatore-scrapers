import csv
import re
#import pdb
import requests
#from lxml import etree
from bs4 import BeautifulSoup as BS
import json
from sgrequests import SgRequests
session = SgRequests()

base_url = 'https://www.maclonline.com/'



def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    }
    
    soup = BS(session.get("https://www.maclonline.com/locations/", headers=headers).text, "lxml")
    for data in soup.find_all("div",{"class":"location-list-item clearfix"}):
        location_name = data['data-title']
        lat = data['data-latitude']
        lng = data['data-longitude']
        store_number = data['data-id']
        
        addr = list(data.stripped_strings)
        del addr[0]
        if "Community" in addr[0] or "Pavilion" in addr[0] :  
            del addr[0]
        street_address = addr[0].replace(",","")
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[1].split()[0]
        zipp = addr[1].split(",")[1].split()[1]
        if street_address == "8890 E 116th Street":
            street_address = "8890 E 116th Street Suite 230"
        if "Phone" not in addr[2]:
            del addr[2]
        phone = addr[2].replace("Phone:","").strip()
        
        del addr[:4]


        if len(addr) > 1:
            if"Monday"in addr[0]:
                hours = addr[0]
            if"Saturday:"in addr[1] or"pm"in addr[1] or"Tuesday"in addr[1] or"Holidays"in addr[1]:
                hours+= " " + addr[1]
            if"Holidays"in addr[2]:
                hours+= " " + addr[2]
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
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours.replace("pm,","pm"))
        store.append("https://www.maclonline.com/locations/")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
