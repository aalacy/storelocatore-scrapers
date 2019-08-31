import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.donrobertojewelers.com"
    locations_url = "/ustorelocator/location/map/?page="
    header = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Host': "www.donrobertojewelers.com",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    body = "ajax=1"
    return_main_object = []
    page_id = 0
    location_id = 0
    cleanr = re.compile('<.*?>')
    while True:
        page_id = page_id + 1
        print(page_id)
        page_reqeust = requests.post(base_url+locations_url+str(page_id),headers=header,data=body)
        locations = page_reqeust.json()["markers"]
        if locations[0]['location_id'] == location_id:
            break
        else:
            location_id = locations[0]['location_id']
            for i in range(len(locations)):
                store_data = locations[i]
                store=[]
                store.append("https://www.donrobertojewelers.com")
                store.append(store_data['title'])
                if store_data["address_zip"] == None or store_data["address_zip"] == "":
                    if len(store_data["address"].split(".")) == 3:
                        store.append(store_data["address"].split(".")[0])
                        store.append(store_data['address'].split(".")[1].split(" ")[1])
                    else:
                        store.append(" ".join(store_data["address"].split(" ")[0:-4]))
                        store.append(" ".join(store_data['address'].split(" ")[-4:-2]))
                    store.append(store_data["address"].split(" ")[-2])
                    store.append(store_data['address'].split(" ")[-1])
                else:
                    store.append(store_data["address_street"])
                    store.append(store_data['address_city'])
                    store.append(store_data['address_state'])
                    store.append(store_data["address_zip"])
                store.append("US")
                store.append(store_data["location_id"])
                store.append(store_data['phone'])
                store.append("don roberto jewelers")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                if re.sub(cleanr, '', store_data["hours"]) == "":
                    store.append("<MISSING>")
                else:
                    store.append(re.sub(cleanr, '', store_data["hours"]))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
