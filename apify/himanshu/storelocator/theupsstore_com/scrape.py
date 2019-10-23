import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    hour_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.theupsstore.com"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 30
    MAX_DISTANCE = 350.0
    zip = search.next_zip()
    while zip:
        result_coords = []
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        print('Pulling zip %s...' % (str(zip)))
        data = "ctl01%24SearchBy=rbLocation&ctl01%24tbSearchText=" + str(zip) + "&ctl01%24tbSearchTextByStore=" + str(zip) + "&ctl01%24hdLatLon=&hdEmailThankYouRedirect=&__EVENTTARGET=ctl01%24btnSearch&__ASYNCPOST=true"
        print(data)
        r = requests.post("https://www.theupsstore.com/tools/find-a-store",headers=headers,data=data)
        soup = BeautifulSoup(r.text,"lxml")
        data = json.loads(soup.find("input",{"id":"MapPointData"})["value"])
        print("stop")
        for store_data in data:
            lat = store_data["Latitude"]
            lng = store_data["Longitude"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.theupsstore.com")
            store.append("<MISSING>")
            store.append(store_data["Address"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["City"])
            store.append(store_data["State"])
            store.append(store_data["Zip"])
            store.append("US")
            store.append(store_data["StoreNum"])
            store.append(store_data["Phone"] if "Phone" in store_data and store_data["Phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            hours_request = requests.get(store_data["StoreURL"],headers=hour_headers)
            hours_soup = BeautifulSoup(hours_request.text,"lxml")
            hours = " ".join(list(hours_soup.find("div",{'class':"Hours--location"}).stripped_strings))
            for hour in hours_soup.find("div",{"class":"Hours--location"}).find_all("div",{"class":"OpenStatus-summary"}):
                hours = hours.replace(" ".join(list(hour.stripped_strings)),"")
            store.append(hours.replace("  "," ") if hours != "" else "<MISSING>")
            store.append(store_data["StoreURL"])
            yield store
        if len(data) < MAX_RESULTS:
            print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
