import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cornerstore_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
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
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
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

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
}

return_main_object = []
addresses = []


def store_handler(store_data,key):
    if store_data["country"] not in ("US","CA","Canada"):
        return
    if store_data["op_status"] != "Open":
        return
    #logger.info("https://www.circlek.com" + store_data["url"])
    #logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~  ",store_data)
    # exit()
    location_request = session.get("https://www.circlek.com" + store_data["url"],headers=headers)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    if location_soup.find("a",{'href':re.compile("tel:")}):
        phone = location_soup.find("a",{'href':re.compile("tel:")}).text.strip()
    else:
        phone = "<MISSING>"
    if location_soup.find("h2",{"class":"heading-small"}):
        street_address = ",".join(list(location_soup.find("h1",{"class":"heading-big"}).stripped_strings)).replace(",,","")
        city = list(location_soup.find("h2",{"class":"heading-small"}).stripped_strings)[0]
        if len(list(location_soup.find("h2",{"class":"heading-small"}).stripped_strings)) > 2:
            state = list(location_soup.find("h2",{"class":"heading-small"}).stripped_strings)[2]
        else:
            state = "<MISSING>"
        if len(state) != 2 and state.isupper():
            state = "<MISSING>"
        store_zip = list(location_soup.find("h2",{"class":"heading-small"}).stripped_strings)[-1]
        if len(store_zip) != 7 and len(store_zip) != 5 and len(store_zip) != 10:
            store_zip = '<MISSING>'
    else:
        street_address = store_data["address"]
        city = store_data["city"]
        state = "<MISSING>"
        store_zip = "<MISSING>"
    if store_data["country"] == "US":
        country = "US"
    else:
        country = "CA"
    store = []
    store.append("http://cornerstore.com/")
    store.append("<MISSING>")
    store.append(" ".join(street_address.split(",")[1:]))
    if store[-1] == "":
        street_address = list(location_soup.find("h1",{"class":"heading-big"}).stripped_strings)[-1]
    if store[-1] == "":
        street_address = list(location_soup.find("h1",{"class":"heading-big"}).find_all("span")[-1].text.stripped_strings)
    if store[-1] == "":
        street_address = "<MISSING>"
    if store[-1] in addresses:
        return
    addresses.append(store[-1])
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append(country)
    if store[-1] == "CA":
        if store[4] == store[5]:
            store[4] = "<MISSING>"
    store.append(key)
    store.append(phone.replace('(','') if phone.replace('(','') else "<MISSING>")
    store.append("Corner Store")
    store.append(store_data["latitude"] if store_data["latitude"] else "<MISSING>")
    store.append(store_data["longitude"] if store_data["longitude"] else "<MISSING>")
    if location_soup.find("div",{"class":"hours-wrapper"}):
        hours = " ".join(list(location_soup.find("div",{"class":"hours-wrapper"}).stripped_strings))
    else:
        hours = "<MISSING>"
    store.append(hours if hours else "<MISSING>")
    store.append("https://www.circlek.com" + store_data["url"])
    for i in range(len(store)):
        if type(store[i]) == str:
            store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
    store = [x.replace("–","-") if type(x) == str else x for x in store]
    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
    return_main_object.append(store)

def fetch_data():
    #logger.info("start")
    r = session.get("https://www.circlek.com/stores_new.php?lat=40.73&lng=-73.5&distance=10000000.00&services=&region=global",headers=headers)
    data = r.json()["stores"]
    #logger.info("start1")
    executor = ThreadPoolExecutor(max_workers=10)
    fs = [ executor.submit(store_handler, data[key],key) for key in data]
    wait(fs)
    executor.shutdown(wait=False)
    for store in return_main_object:
        #logger.info("~~~~~~~~~~~~~~~~~ ",store)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
