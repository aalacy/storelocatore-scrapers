import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import unicodedata
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
}

addresses = []

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","raw_address"])
        # Body
        for row in data:
            if row[-1] in addresses:
                continue
            addresses.append(row[-1])
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

locaiton_urls = []
store_urls = []
return_main_object = []
base_url = "https://www.pga.com"

def state_handler(url):
    state_request = request_wrapper(url,'get',headers=headers)
    state_soup = BeautifulSoup(state_request.text,"lxml")
    for location in state_soup.find("ul").find_all("a"):
        if base_url + location["href"] in locaiton_urls:
            continue
        locaiton_urls.append(base_url + location["href"])

def location_heandler(url):
    location_request = request_wrapper(url,'get',headers=headers)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    for store in location_soup.find_all("a",{"data-gtm-content-type":"Facility"}):
        if base_url + store["href"] in store_urls:
            continue
        store_urls.append(base_url + store["href"])

def store_handler(url):
    # print(url)
    store_request = request_wrapper(url,'get',headers=headers)
    if store_request == None:
        return
    store_soup = BeautifulSoup(store_request.text,"lxml")
    name = store_soup.find("h4").text
    location_details = list(store_soup.find("h4").parent.find("div").stripped_strings)
    street_address = " ".join(list(store_soup.find("h4").parent.find("div").find("div").stripped_strings))
    if street_address == "":
        return
    phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location_details[-1])
    if phone_split:
        phone = location_details[-1]
    else:
        phone = "<MISSING>"
    store = []
    store.append("https://www.pga.com")
    store.append(name)
    store.append("<INACCESSIBLE>")
    store.append("<INACCESSIBLE>")
    store.append("<INACCESSIBLE>")
    store.append("<INACCESSIBLE>")
    store.append("US")
    store.append(url.split("/")[-1])
    store.append(phone) # phone
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append("<MISSING>")    
    store.append(url)
    store.append(street_address)
    for i in range(len(store)):
        if type(store[i]) == str:
            store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
    store = [x.replace("–","-") if type(x) == str else x for x in store]
    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
    return_main_object.append(store)
    # print(len(return_main_object))

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    r = requests.get("https://www.pga.com/play",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    state_urls = []
    for state in soup.find("h4",text=re.compile("Search for Courses by State")).parent.find_all("a"):
        if base_url + state["href"] in state_urls:
            continue
        state_urls.append(base_url + state["href"])
    executor = ThreadPoolExecutor(max_workers=10)
    fs = [ executor.submit(state_handler, url) for url in state_urls]
    wait(fs)
    executor.shutdown(wait=False)
    # print(locaiton_urls[0])
    executor = ThreadPoolExecutor(max_workers=10)
    fs = [ executor.submit(location_heandler, url) for url in locaiton_urls]
    wait(fs)
    executor.shutdown(wait=False)
    # print(store_urls[0])
    executor = ThreadPoolExecutor(max_workers=10)
    fs = [ executor.submit(store_handler, url) for url in store_urls]
    wait(fs)
    executor.shutdown(wait=False)
    for store in return_main_object:
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()