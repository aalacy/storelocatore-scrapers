import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgChrome

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
    
    base_link = "https://www.golden1.com/atm-branch-finder"
    driver = SgChrome().chrome()
    driver.get(base_link)

    cookies = driver.get_cookies()
    cookie= ""
    for cook in cookies:
        cookie = cookie + cook["name"] + "=" + cook["value"] + "; "

    cookie = cookie.strip()[:-1]

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
            'cookie': cookie,
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

    driver.close()  
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
