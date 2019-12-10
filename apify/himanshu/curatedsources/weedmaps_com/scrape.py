import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip

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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 20
    MAX_DISTANCE = 100
    urls = []
    addresses = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r = requests.get("https://api-g.weedmaps.com/discovery/v1/suggestions?latlng=" + str(x) + "%2C" + str(y) + "&q=*&types=dispensary%2C&dispensary_max_size=20",headers=headers)
        data = r.json()["dispensary"]
        store_count = 0
        for store_data in data:
            page_url = "https://weedmaps.com/dispensaries/" + str(store_data["slug"]) + "/about"
            if page_url in urls:
                continue
            urls.append(page_url)
            location_request = requests.get(page_url,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            location_data = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text)
            result_coords.append((location_data["geo"]["latitude"],location_data["geo"]["longitude"]))
            address = location_data["address"]
            hours = " ".join(list(location_soup.find("div",{"class":re.compile("components__OpenHours")}).stripped_strings))
            store = []
            store.append("https://weedmaps.com")
            store.append(location_data["name"])
            store.append(address["streetAddress"] if address["streetAddress"] else "<MISSING>")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store_count = store_count + 1
            store.append(address["addressLocality"] if address["addressLocality"] else "<MISSING>")
            store.append(address["addressRegion"] if address["addressRegion"] else "<MISSING>")
            store.append(address["postalCode"] if address["postalCode"] else "<MISSING>")
            postalCode = store[-1]
            ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',postalCode.upper())
            if ca_zip_split:
                store.append("CA")
            else:
                store.append("US")
            if str(store[-2]) == "1":
                store[-1] = "CA"
                store[-2] = "<MISSING>"
            if store[-1] == "US":
                if store[-2].replace("-","").replace(" ","").isdigit() == False:
                    continue
                if store[5] in store[2] and store[3] in store[2]:
                    store[2] = store[2].split(",")[0]
            if store[-1] == "CA":
                store[-2] = store[-2].upper()
            store.append("<MISSING>")
            phone = ""
            phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location_data["telephone"])
            if phone_split:
                phone = phone_split[0]
            store.append(phone.replace(")","") if phone else "<MISSING>")
            store.append("dispensary")
            store.append(location_data["geo"]["latitude"])
            store.append(location_data["geo"]["longitude"])
            store.append(hours if hours else "<MISSING>")
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # print(store)
            yield store
        if store_count < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif store_count == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 20
    MAX_DISTANCE = 100
    urls = []
    addresses = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r = requests.get("https://api-g.weedmaps.com/discovery/v1/suggestions?latlng=" + str(x) + "%2C" + str(y) + "&q=*&types=delivery%2C&delivery_max_size=20",headers=headers)
        data = r.json()["delivery"]
        store_count = 0
        for store_data in data:
            page_url = "https://weedmaps.com/deliveries/" + str(store_data["slug"]) + "/about"
            if page_url in urls:
                continue
            urls.append(page_url)
            location_request = requests.get(page_url,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            location_data = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text)
            result_coords.append((location_data["geo"]["latitude"],location_data["geo"]["longitude"]))
            address = location_data["address"]
            hours = " ".join(list(location_soup.find("div",{"class":re.compile("components__OpenHours")}).stripped_strings))
            store = []
            store.append("https://weedmaps.com")
            store.append(location_data["name"])
            store.append(address["streetAddress"] if address["streetAddress"] else "<MISSING>")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store_count = store_count + 1
            store.append(address["addressLocality"] if address["addressLocality"] else "<MISSING>")
            store.append(address["addressRegion"] if address["addressRegion"] else "<MISSING>")
            store.append(address["postalCode"] if address["postalCode"] else "<MISSING>")
            postalCode = store[-1]
            ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',postalCode.upper())
            if ca_zip_split:
                store.append("CA")
            else:
                store.append("US")
            if str(store[-2]) == "1":
                store[-1] = "CA"
                store[-2] = "<MISSING>"
            if store[-1] == "US":
                if store[-2].replace("-","").replace(" ","").isdigit() == False:
                    continue
                if store[5] in store[2] and store[3] in store[2]:
                    store[2] = store[2].split(",")[0]
            if store[-1] == "CA":
                store[-2] = store[-2].upper()
            store.append("<MISSING>")
            phone = ""
            phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location_data["telephone"])
            if phone_split:
                phone = phone_split[0]
            store.append(phone.replace(")","") if phone else "<MISSING>")
            store.append("delivery")
            store.append(location_data["geo"]["latitude"])
            store.append(location_data["geo"]["longitude"])
            store.append(hours if hours else "<MISSING>")
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # print(store)
            yield store
        if store_count < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif store_count == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
