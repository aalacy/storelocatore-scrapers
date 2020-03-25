# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Host": "www.bjsrestaurants.com",
        "Referer":"https://www.bjsrestaurants.com/locations",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    }

    base_url = "https://www.bjsrestaurants.com"
    r = session.get("https://www.bjsrestaurants.com/sitemap", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("a"):
        if "/locations/" not in link['href']:
            continue
        state_url = base_url+link['href']
        location_r = session.get(state_url)
        location_soup = BeautifulSoup(location_r.text, "lxml")
        for location in location_soup.find_all("location-order-online-button"):
            data = json.loads(location['data-location'])
            location_name = data['site_name']
            street_address = data['address']
            city = data['city']
            state = data['state']
            zipp = data['zip_code']
            country_code = "US"
            store_number = data['id']
            phone = data['phone']
            location_type = 'Restaurant'
            latitude = data['latitude']
            longitude = data['longitude']
            hours = data['monday_time'].split(" ")[-1] +" "+ " ".join(data['monday_time'].split(" ")[:-1])+" "+\
                data['tuesday_time'].split(" ")[-1] +" "+ " ".join(data['tuesday_time'].split(" ")[:-1])+" "+\
                    data['wednesday_time'].split(" ")[-1] +" "+ " ".join(data['wednesday_time'].split(" ")[:-1])+" "+\
                        data['thursday_time'].split(" ")[-1] +" "+ " ".join(data['thursday_time'].split(" ")[:-1])+" "+\
                            data['friday_time'].split(" ")[-1] +" "+ " ".join(data['friday_time'].split(" ")[:-1])+" "+\
                                data['saturday_time'].split(" ")[-1] +" "+ " ".join(data['saturday_time'].split(" ")[:-1])+" "+\
                                    data['sunday_time'].split(" ")[-1] +" "+ " ".join(data['sunday_time'].split(" ")[:-1])
            page_url = state_url+"/"+str(data['slug'])

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
