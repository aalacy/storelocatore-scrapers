import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def fetch_data():
    data=[];hours_of_operation=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[];country=[];store_no=[]
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    page = 0
    while True:
        r = requests.get("https://keyfoodstores.keyfood.com/store/keyFood/en/store-locator?q=11756&page=" + str(page) + "&radius=5000000000&all=true",headers=headers)
        try:
	        store_data = r.json()["data"]
        except ValueError:
	        break
        for content in store_data:
            location_name.append(content["displayName"])
            if content["line2"]:
                street_address.append(content["line1"] + " " + content["line2"])
            else:
                street_address.append(content["line1"])
            city.append(content["town"])
            state.append(content["state"])
            zipcode.append(content["postalCode"])
            country.append("US")
            store_no.append(content["name"])
            phone.append(content["phone"] if content["phone"] else "<MISSING>")
            latitude.append(content["latitude"])
            longitude.append(content["longitude"])
            hours=""
            for hour in content["openings"]:
                hours = hours + " " + hour + " " + content["openings"][hour]
            hours_of_operation.append(hours if hours else "<MISSING>")

        page = page + 1
    for n in range(0,len(location_name)): 
        data.append([
            'http://superfreshfood.com',
            '<MISSING>',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_no[n],
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
