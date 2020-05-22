import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    locator_domain = "https://www.lifecareservices-seniorliving.com/"
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
    raw_address = ""
    hours_of_operation = ""
    location_url = "https://www.lifecareservices-seniorliving.com/"
    # data="pg=1&action=get_communities&gd_nonce=ce7ea9f2e6"
    headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    
# 
    }
    data = {
        'pg': '1',
        'action': 'get_communities',
        'gd_nonce': 'eef8cb073c'
    }
    # payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"pg\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nget_communities\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"gd_nonce\"\r\n\r\nce7ea9f2e6\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    r = session.post("https://www.lifecareservices-seniorliving.com/wp-admin/admin-ajax.php",headers=headers,data=data).json()
    for ut in r['results']:
        soup1 = BeautifulSoup(ut['html'], "html5lib")
        for data in soup1.find_all("div",{"class":"cmnty-results-address"}):
            full = list(data.find("p",{"class":"address"}).stripped_strings)
            if full[0]=="Information Center":
                del full[0]
            city = list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[0]
            state= list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[-1].strip().split(" ")[0]
            zipp = list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[-1].strip().split(" ")[-1]
            street_address = ' '.join(full[:-1])
            location_name=data.find("h5",{"class":"cmnty-results-item-heading"}).text.strip()
            phone = list(data.stripped_strings)[-2].replace("Chicago,       IL","<MISSING>").replace("Austin,       TX       78731","<MISSING>").replace("West Lafayette,       IN       47906-1431","<MISSING>").replace("Wheaton,       IL       60187","<MISSING>").replace("Bridgewater,       NJ       08807","<MISSING>").replace("Atchison,       KS       66002","<MISSING>")
            # print(phone)
            try:
                page_url =(data.find("h5",{"class":"cmnty-results-item-heading"}).find("a")['href'])
            except:
                page_url="<MISSING>"
            latitude = ut['latitude']
            # print(latitude)
            longitude = ut['longitude']
            store_number="<MISSING>"
            location_type="<MISSING>"
       
            hours_of_operation="<MISSING>"
            store = ["https://www.lifecareservices-seniorliving.com", location_name, street_address.encode('ascii', 'ignore').decode('ascii').strip(), city, state, zipp.replace("IL","<MISSING>"), country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
