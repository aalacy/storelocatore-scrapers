import csv
import requests
from bs4 import BeautifulSoup
import re
import json
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
# def hasNumbers(inputString):
#     return any(char.isdigit() for char in inputString)



def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    base_url = "https://gomart.com/"

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
    raw_address = ""
    hours_of_operation = ""
    page_url =""

    r = requests.get("https://gomart.com/locations/",headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    # print(soup.prettify())
    script =soup.find(lambda tag: (tag.name == "script") and "window.map.addMarker" in tag.text).text.split('LatLngBounds();')[1].split('var storeList')[0].split('window.map.addMarker(')
    for x in script:
        x_list = x.replace(');',"").strip()
        removal_list = [' ', '\t', '\n']
        for s in removal_list:
            x_list = x_list.replace(s, ' ')
        val = x_list.split('data:')[-1].split('},')[0]+"}"
        if "}" !=val:
            info = json.loads(val)
            location_name = info['name']
            street_address = info['address']
            city = info['city']
            state = info['state']
            zipp = info['zip']
            phone = info['phone']
            latitude = info['latitude']
            longitude = info['longitude']
            location_type = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            hours_of_operation = "<MISSING>"
            page_url = "https://gomart.com/company/"+"-".join(info['name'].lower().split())
             
        
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
