import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('eyeelements_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="UTF-8") as output_file:
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
    
    return_main_object = []
    addresses = []
    cords = sgzip.coords_for_radius(50)
    for cord in cords:
        # logger.info("https://www.clarksoneyecare.com/wp-json/352inc/v1/locations/coordinates?lat="+str(cord[0])+"&lng="+str(cord[1]))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        r = request_wrapper("https://www.clarksoneyecare.com/wp-json/352inc/v1/locations/coordinates?lat="+str(cord[0])+"&lng="+str(cord[1]),'get',headers=headers)
        if r == None:
            continue
        if r.text == "null":
            continue
        else:
            try:
                data = r.json()
            except:
                continue
            
            for store_data in data:
                store = []
                store.append("https://www.eyeelements.com")
                store.append(store_data["name"])
                store.append(store_data["address1"] + " " + store_data['address2'] + " " + store_data["address3"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zip_code"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["phone_number"] if store_data["phone_number"] != "" and store_data["phone_number"] != None else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                location_request = request_wrapper(store_data["permalink"],'get',headers=headers)
                if location_request == None:
                    continue
                location_soup = BeautifulSoup(location_request.text,"lxml")
                hours = " ".join(list(location_soup.find("div",{"class":"col-lg-4 times"}).stripped_strings))
                store.append(hours if hours != "" else "<MISSING>")
                store.append(store_data["permalink"])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
