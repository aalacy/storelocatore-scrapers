from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
import re

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    base_link = "https://www.wagamama.com/restaurants"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    data = []

    locator_domain = "wagamama.com"
    items = base.find_all(class_="restaurant-hub__results-item") 
    for item in items:
        location_name = item.h2.text.title()
        print(location_name)

        zip_code = item.find(class_="restaurant-hub__postcode").text.strip()
        country_code = "GB"
        store_number = item['data-id']
        phone = item.find(class_="restaurant-hub__phone").text.strip()
        if not phone:
            phone = "<MISSING>"
        latitude = item['data-lat']
        longitude = item['data-lng']

        link = "https://www.wagamama.com" + item.find_all("a")[-1]['href']
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        street_address = ""
        address_lines = base.find_all(class_="restaurant-details__address-line")
        for address_line in address_lines[:-2]:
            street_address = (street_address + " " + address_line.text.strip()).strip()
        street_address = street_address.title().replace("'S","'s")
        city = address_lines[-2].text.strip().title()
        if not street_address:
            street_address = " ".join(city.split(",")[:-1]).strip()
            city = city.split(",")[-1].strip()

        street_address = (re.sub(' +', ' ', street_address)).strip()
        state = "<MISSING>"

        script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
        store_data = json.loads(script)
        location_type = ""
        feats = store_data['amenityFeature']
        for feat in feats:
            location_type = location_type + ", " + feat['name']
        location_type = location_type[2:].strip()
        hours = base.find(class_="restaurant-find-us__opening-times-inner").table.text.replace("\n"," ").strip()
        hours_of_operation = (re.sub(' +', ' ', hours)).strip()

        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
