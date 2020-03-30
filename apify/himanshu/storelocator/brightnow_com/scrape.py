import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import unicodedata


session = SgRequests()

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

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.brightnow.com"
    r = request_wrapper("https://api.smilebrands.com/public/facility/geoRegions",'get',headers=headers)
    data = r.json()["data"]
    addresses = []
    for state in data:
        state_request = request_wrapper("https://api.smilebrands.com/public/facility/search/state/" + state["state"].lower(),'get',headers=headers)
        state_data = state_request.json()["data"]
        for store_data in state_data:
            store = []
            store.append("https://www.brightnow.com")
            store.append(store_data["contactName"].replace('>',''))
            store.append((store_data["address"] +" "+ str(store_data["careOf"])).strip())
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["zip"])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phoneNumber"])
            store.append(store_data["contactName"].split("-")[0].strip().replace('!',''))
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            location_request = request_wrapper("https://api.smilebrands.com/public/facility/id/" + str(store_data["id"]),'get',headers=headers)
            location_data = location_request.json()["data"]
            if location_data == None:
                continue
            hours = ""
            if 'sundayHours' in location_data and location_data["sundayHours"] != None:
                hours = hours + " SUNDAY " + location_data["sundayHours"]
            if 'mondayHours' in location_data and location_data["mondayHours"] != None:
                hours = hours + " MONDAY " + location_data["mondayHours"]
            if 'tuesdayHours' in location_data and location_data["tuesdayHours"] != None:
                hours = hours + " TUESDAY " + location_data["tuesdayHours"]
            if 'wednesdayHours' in location_data and location_data["wednesdayHours"] != None:
                hours = hours + " WEDNESDAY " + location_data["wednesdayHours"]
            if 'thursdayHours' in location_data and location_data["thursdayHours"] != None:
                hours = hours + " THURSDAY " + location_data["thursdayHours"]
            if 'fridayHours' in location_data and location_data["fridayHours"] != None:
                hours = hours + " FRIDAY " + location_data["fridayHours"]
            if 'saturdayHours' in location_data and location_data["saturdayHours"] != None:
                hours = hours + " SATURDAY " + location_data["saturdayHours"]
            store.append(hours if hours != "" else "<MISSING>")
            for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            # print(store)


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
