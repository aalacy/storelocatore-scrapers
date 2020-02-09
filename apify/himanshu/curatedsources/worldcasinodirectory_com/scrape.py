import csv
import requests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import calendar


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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

    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    #     "accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

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

            try:
                r_loc = requests.get(page_url, headers=headers)
                soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                street_address = list(soup_loc.find('h1', {'itemprop': 'name'}).find_next(
                    'h3').stripped_strings)[0].split(',')[-3]
                # print(street_address)
                location_type = "<MISSING>"
                info = list(soup_loc.find(
                    'div', class_='contentInGreyBlock contactInfo clearfix').stripped_strings)
                if info == []:
                    # print(page_url)
                    phone = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    zipp = "<MISSING>"
                else:
                    ca_zip_list = re.findall(
                        r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(info)))
                    if ca_zip_list:
                        zipp = ca_zip_list[0].strip()
                    else:
                        zipp = "<MISSING>"
                    phone_list = re.findall(re.compile(
                        ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(info)))
                    if phone_list:
                        phone = phone_list[0].strip()
                    else:
                        phone = "<MISSING>"
                    if "Casino hours" in " ".join(info):
                        hours_of_operation = "Casino hours  " + \
                            " ".join(info).split('Casino hours')[1]
                        # print(hours_of_operation)
                    else:
                        hours_of_operation = "<MISSING>"
                        # print(info)
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            except:
                street_address = "<MISSING>"
                phone = "<MISSING>"
                zipp = "<MISSING>"
                hours_of_operation = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x == "" or x == None else x for x in store]
            # attr = store[2] + " " + store[3]
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

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
            try:
                r_loc = requests.get(page_url, headers=headers)
                soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                street_address = list(soup_loc.find('h1', {'itemprop': 'name'}).find_next(
                    'h3').stripped_strings)[0].split(',')[-3]
                location_type = "<MISSING>"
                info = list(soup_loc.find(
                    'div', class_='contentInGreyBlock contactInfo clearfix').stripped_strings)
                if info == []:
                    # print(page_url)
                    phone = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    zipp = "<MISSING>"
                else:
                    us_zip_list = re.findall(re.compile(
                        r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(info)))
                    if us_zip_list:
                        zipp = us_zip_list[-1].strip()
                    else:
                        zipp = "<MISSING>"
                    phone_list = re.findall(re.compile(
                        ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(info)))
                    if phone_list:
                        phone = phone_list[0].strip()
                    else:
                        phone = "<MISSING>"
                    if "Casino hours" in " ".join(info):
                        hours_of_operation = "Casino hours  " + \
                            " ".join(info).split('Casino hours')[1]
                        # print(hours_of_operation)
                    else:
                        hours_of_operation = "<MISSING>"
                        # print(info)
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            except:
                street_address = "<MISSING>"
                phone = "<MISSING>"
                zipp = "<MISSING>"
                hours_of_operation = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x == "" or x == None else x for x in store]
            # attr = store[2] + " " + store[3]
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
