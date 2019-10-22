import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from urllib3.exceptions import InsecureRequestWarning
import time
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def write_output(data):
    with open('data.csv', mode='w',encoding="UTF-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    cords = sgzip.coords_for_radius(50)
    for cord in cords:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        while True:
            cord_count = 0
            try:
                r = requests.get("https://www.rinkoveyecare.com/wp-json/352inc/v1/locations/coordinates?lat=" + str(cord[0]) + "&lng=" + str(cord[1]),headers=headers,verify=False)
                break
            except:
                time.sleep(2)
                cord_count = cord_count + 1
                if cord_count > 10:
                    # print("failed to get this cord " + str("https://www.rinkoveyecare.com/wp-json/352inc/v1/locations/coordinates?lat=" + str(cord[0]) + "&lng=" + str(cord[1])))
                    break
                continue
        if r.text == "null":
            continue
        else:
            data = r.json()
            for store_data in data:
                store = []
                store.append("https://www.rinkoveyecare.com")
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
                location_count = 0
                while True:
                    try:
                        location_request = requests.get(store_data["permalink"],headers=headers,verify=False)
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        hours = " ".join(list(location_soup.find("div",{"class":"col-lg-4 times"}).stripped_strings))
                        store.append(hours if hours != "" else "<MISSING>")
                        store.append(store_data["permalink"])
                        yield store
                        break
                    except:
                        time.sleep(2)
                        location_count = location_count + 1
                        if location_count > 10:
                            # print("failed to get this location " + str(store_data["permalink"]))
                            break
                        continue
                

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
