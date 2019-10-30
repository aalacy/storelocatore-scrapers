import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from random import randrange
import os
import unicodedata

session = requests.Session()
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 25
    MAX_DISTANCE = 75.0
    coord = search.next_coord()
    while coord:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        random_number = randrange(5,10)
        time.sleep(random_number)
        r = session.get("https://bellca.know-where.com/bellca/cgi/selection?lang=en&loadedApiKey=main&ll=" + str(coord[0]) + "%2C" + str(coord[1]) + "&stype=ll&async=results",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        lat = r.text.split("poilat")[1].split(",")[0].replace('"',"").replace(":","")
        lng = r.text.split("poilon")[1].split(",")[0].replace('"',"").replace(":","")
        for location in soup.find_all("li",{"class":"rsx-sl-store-list-store"}):
            if location.find('b'):
                name = location.find('b').text.strip()
            else:
                name = "<MISSING>"
            store_data = json.loads(location.find("script",{"type":"application/ld+json"}).text)
            address = store_data["address"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.bell.ca")
            store.append(name if name[-1] != ":" else "<MISSING>")
            store.append(address["streetAddress"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(address["addressLocality"]  if "addressLocality" in address else "<MISSING>")
            store.append(address["addressRegion"]  if "addressRegion" in address else "<MISSING>")
            store.append(address["postalCode"][:3] + " " + address["postalCode"][3:] if "postalCode" in address else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["telephone"] if "telephone" in store_data and store_data["telephone"] != "" and store_data["telephone"] != None  else "<MISSING>")
            store.append("<MISSING>")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            hours = " ".join(list(location.find("ul",{"class":'rsx-sl-store-list-hours'}).stripped_strings))
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<MISSING>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # print(store)
            yield store
        if len(soup.find_all("li",{"class":"rsx-sl-store-list-store"})) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(soup.find_all("li",{"class":"rsx-sl-store-list-store"})) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()