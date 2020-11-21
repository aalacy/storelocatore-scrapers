import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    HEADERS = {
            'authority': 'www.golden1.com',
            'method': 'POST',
            'path': '/api/BranchLocator/GetLocations',
            'scheme': 'https',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'content-length': '275',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': 'g1web-cookie-RL=2744297664.20480.0000; ak_bmsc=75E0635CAA910EC8196521F06CC3203F17C91665744400001CFEB85F08034D67~plZVdKTDeGjwqpHQZRhauM8kmaVBQhGFPyLvvVn36m1PZ5SXmUOJn9q1qY94+i03dFBja3xcyguDJb+pXocjpLJejB4OEwT8fveKt3GkjfQPzyzlJUauymmwhwYLAF80LzYCMuM5qqVFPgA7J02BIPOfcJV7fdBMEn/0XhqBGfEClvW4X1nTzHPoXOJABtAASF0l8J5INY48E9rxK8+G6/W4YvdkT373TXqwUtj8mKLSE=; g1web-cookie-HQ=2744232128.20480.0000; _gcl_au=1.1.1023096693.1605959198; _ga=GA1.2.698997750.1605959198; _gid=GA1.2.1812316788.1605959198; __utma=123164701.698997750.1605959198.1605959198.1605959198.1; __utmc=123164701; __utmz=123164701.1605959198.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt_UA-1815591-1=1; __utmb=123164701.2.10.1605959198; bm_sv=B289FC477E85E0924DFA2CE7F54DBEFC~GT6vk3vxVnitM0eeczY5HdYS2lhjHdxsrQH+35YQDCa8cZ1Z1mC8AEG7HRgmdNwk7ZxZhPtJeBKvGD0IzZR+FoWCgMWsycnNRJQ1lvqgVUM8GWpXj6p/3ndKaUz4oRCkbJcGFxD8tz1EaZJOBIy5H90PSGgiI+Xfz+lxPO3L4Lk=',
            'origin': 'https://www.golden1.com',
            'referer': 'https://www.golden1.com/atm-branch-finder',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

    return_main_object = []
    base_url = "https://www.golden1.com/"
    addresses = []

    data = "golden1branches=true&golden1homecenters=false&golden1atm=false&sharedbranches=false&sharedatm=false&swlat=32.92592150627013&swlng=-125.83287772749976&nelat=45.974237591040335&nelng=-108.89642295455054&centerlat=39.75807600279975&centerlng=-117.36465034102515&userlat=&userlng="
    location_url = 'https://www.golden1.com/api/BranchLocator/GetLocations'
    data = session.post(location_url, headers=HEADERS, data=data).json()

    for json_data in data['locations']:
        street_address = json_data['address']
        city =json_data['city']
        zipp = json_data['zip']
        hours = json_data['hours']
        location_name = json_data['title']
        latitude =  json_data['lat']
        longitude=  json_data['lng']
        page_url = json_data['imageUrl']
        location_type = '<MISSING>'
        store_number = json_data['branchAppUrl'].split("=")[-1]

        hours_of_operation = " ".join(list(BeautifulSoup(hours, "lxml").stripped_strings)).replace("\\n"," ")
        store = []        
        store.append("https://www.golden1.com")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append('CA')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append(store_number if store_number else '<MISSING>')
        store.append('<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append('<MISSING>')
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        return_main_object.append(store)
        
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
