import csv
import requests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import calendar


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.coords_for_radius(50)
    addresses = []

    
    # it will used in store data.
    locator_domain = "https://www.worldcasinodirectory.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'}
    # CA location

    r = requests.get(
        'https://www.worldcasinodirectory.com/api?country=6251999&offset=0&limit=10000&order[slots]=DESC', headers=headers).json()
    for loc in r['items']:
        if loc['coming_soon'] == False:
            store_number = loc['id']
            location_name = loc['name']
            country_code = loc['location']['country']['iso']
            state = loc['location']['state']['name']
            city = loc['location']['city']['name']
            longitude = loc['location']['longitude']
            latitude = loc['location']['latitude']
            page_url = "https://www.worldcasinodirectory.com/casino/" + \
                loc['slug']
            if page_url:
                try:
                    r_loc = requests.get(page_url, headers=headers)
                    soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                    try:
                        hours_of_operation = " ".join(list(soup_loc.find("div",class_="hotel-hours").stripped_strings))
                    except:
                        hours_of_operation = "<MISSING>"
                    try:
                        phone = soup_loc.find("span",{"itemprop":"telephone"}).text.replace("=","").replace("=+","").strip()
                    except:
                        phone = "<MISSING>"
                    try:
                        street_address = " ".join(" ".join(list(soup_loc.find("span",{"itemprop":"address"}).stripped_strings)).split(",")[:-3]).replace("Grey Eagle Casino & Bingo","").strip()
                    except:
                        street_address = "<MISSING>"
                    try:
                        zipp = " ".join(" ".join(list(soup_loc.find("span",{"itemprop":"address"}).stripped_strings)).split(",")[-2].split()[1:]).strip()
                    except:
                        zipp = "<MISSING>"
                except:
                    hours_of_operation = "<MISSING>"
                    phone= "<MISSING>"
                    street_address = "<MISSING>"
                    zipp = "<MISSING>"
                


            location_type = "Casino"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x == "" or x == None else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # attr = store[2] + " " + store[3]
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            yield store
    #### US Location #####
    r = requests.get(
        'https://www.worldcasinodirectory.com/api?country=6252001&offset=0&limit=20000&order[slots]=DESC', headers=headers).json()
    for loc in r['items']:
        if loc['coming_soon'] == False:
            store_number = loc['id']
            location_name = loc['name']
            country_code = loc['location']['country']['iso']
            state = loc['location']['state']['name']
            city = loc['location']['city']['name']
            longitude = loc['location']['longitude']
            latitude = loc['location']['latitude']
            page_url = "https://www.worldcasinodirectory.com/casino/" + \
                loc['slug']
            if page_url:
                try:
                    r_loc = requests.get(page_url, headers=headers)
                    soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                    try:
                        hours_of_operation = " ".join(list(soup_loc.find("div",class_="hotel-hours").stripped_strings))
                    except:
                        hours_of_operation = "<MISSING>"
                    try:
                        phone = soup_loc.find("span",{"itemprop":"telephone"}).text.replace("=","").replace("=+","").strip()
                    except:
                        phone = "<MISSING>"
                    try:
                        street_address = " ".join(" ".join(list(soup_loc.find("span",{"itemprop":"address"}).stripped_strings)).split(",")[:-3]).strip()
                    except:
                        street_address = "<MISSING>"
                    try:
                        zipp = " ".join(" ".join(list(soup_loc.find("span",{"itemprop":"address"}).stripped_strings)).split(",")[-2].split()[1:]).strip()
                    except:
                        zipp = "<MISSING>"
                except:
                    hours_of_operation = "<MISSING>"
                    phone= "<MISSING>"
                    street_address = "<MISSING>"
                    zipp = "<MISSING>"
            location_type = "Casino"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x == "" or x == None else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # attr = store[2] + " " + store[3]
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
