import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from random import randrange
import platform
import time
import sgzip
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nationalcashadvance_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
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

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 10
    MAX_DISTANCE = 50
    coord = search.next_coord()
    while coord:
        result_coords = []
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        # r = session.get("https://www.nationalcashadvance.com/locations/results/11756/34.9918283/-90.0196623/50/",headers=headers)
        #logger.info("https://www.nationalcashadvance.com/locations/results/11756/" + str(x) + "/" + str(y) + "/50/")
        r = request_wrapper("https://www.nationalcashadvance.com/locations/results/11756/" + str(x) + "/" + str(y) + "/50/","get",headers=headers)
        if r == None:
            coord = search.next_coord()
            continue
        soup = BeautifulSoup(r.text,"lxml")
        for script in soup.find_all("script"):
            if "new google.maps.Marker(" in script.text:
                geo_script = script.text
                break
        count = 0
        for location in soup.find_all("li",{"class":"location"}):
            count = count + 1
            name = " ".join(list(location.find("h2").stripped_strings))
            store_id = name.split("#")[1]
            geo_coord = geo_script.split("marker"+str(count))[1].split('new google.maps.LatLng(')[1].split(")")[0]
            lat = geo_coord.split(",")[0]
            lng = geo_coord.split(",")[1]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.nationalcashadvance.com")
            store.append(name)
            address = list(location.find("span").stripped_strings)
            store.append(address[0])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(address[1].split(",")[0])
            store_zip_split = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),address[1])
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            state_split = re.findall("([A-Z]{2})",address[1])
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            store.append(state if state else "<MISSING>")
            store.append(store_zip if store_zip else "<MISSING>")
            store.append("US")
            store.append(store_id)
            phone_text = " ".join(address)
            phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),phone_text)
            if phone_split:
                phone = phone_split[-1]
            else:
                phone = "<MISSING>"
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            hours = " ".join(list(location.find("div",{"class":"hours"}).stripped_strings))
            store.append(hours if hours else "<MISSING>")
            page_url = "https://www.nationalcashadvance.com/locations/directions/store-" + str(store_id)
            store.append(page_url)
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            #logger.info(store)
            yield store
        if len(soup.find_all("li",{"class":"location"})) < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(soup.find_all("li",{"class":"location"})) == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
