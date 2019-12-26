# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 8
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.selectmedical.com/"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        # location_url = "https://api.honda.ca/dealer/H/Live/dealers/" + str(lat) + "/" + str(
        #     lng) + "/with-driving-distance"
        i = 0
        while True:
            location_url = "https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&sig=&autoFireSearch=true&v={D2D3D65E-3A18-43DD-890F-1328E992446A}&p=8&g=" + str(
                lat) + "|" + str(lng) + "&o=Distance,Ascending&e=" + str(i)
            # print(location_url)
            try:
                r = requests.get(location_url, headers=headers)
                json_data = r.json()
            except:
                continue
            # r_utf = r.text.encode('ascii', 'ignore').decode('ascii')
            # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")

            # json_data = json.loads(r_utf)
            # print("json_Data === " + str(json_data))
            # it always need to set total len of record.
            current_results_len = int(len(json_data["Results"]))
            # print("current_results_len === " + str(current_results_len))

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            hours_of_operation = "<INACCESSIBLE>"
            if json_data["Results"] != []:
                for location in json_data["Results"]:

                    soup = BeautifulSoup(location['Html'], "lxml")
                    try:
                        location_name = soup.find('span', {
                                                  'class': 'location-title'}).text.encode('ascii', 'ignore').decode('ascii').strip()
                    except:
                        location_name = "<MISSING>"
                    try:
                        page_url = soup.find(
                            'span', {'class': 'location-title'}).find("a")["href"]

                    except:
                        page_url = "<MISSING>"

                    add1 = ''
                    add2 = ''
                    if soup.find('div', {'class': 'field-address'}) != None:
                        add1 = soup.find(
                            'div', {'class': 'field-address'}).text

                    if soup.find('div', {'class': 'field-address2'}) != None:
                        add2 = soup.find('div', {
                                         'class': 'field-address2'}).text.encode('ascii', 'ignore').decode('ascii').strip()
                    street_address = add1 + ',' + add2
                    try:
                        city = soup.find('span', {
                                         'class': 'field-city'}).text.encode('ascii', 'ignore').decode('ascii').strip()
                    except:
                        city = "<MISSING>"
                    try:
                        state = soup.find('span', {
                                          'class': 'field-state'}).text.encode('ascii', 'ignore').decode('ascii').strip()
                    except:
                        state = "<MISSING>"
                    try:
                        zipp = soup.find('span', {
                            'class': 'field-zip'}).text.encode('ascii', 'ignore').decode('ascii').strip()
                    except:
                        zipp = "<MISSING>"
                    try:
                        phone = soup.find('div', {
                            'class': 'phone-container'}).text.encode('ascii', 'ignore').decode('ascii').strip()
                    except:
                        phone = "<MISSING>"
                    try:
                        latitude = str(location['Geospatial']['Latitude']).encode(
                            'ascii', 'ignore').decode('ascii').strip()
                        longitude = str(location['Geospatial']['Longitude']).encode(
                            'ascii', 'ignore').decode('ascii').strip()
                    except:
                        latitude = "<MISSING>"
                        longitude = "<MISSING>"
                    # page_url = location_url
                    # print("location ==== " + str(location))
                    # do your logic.

                    result_coords.append((latitude, longitude))
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    # store = [x.strip() if x else "<MISSING>" for x in store]
                    if str(store[2]) + str(store[-3]) not in addresses:
                        addresses.append(str(store[2]) + str(store[-3]))
                        store = [str(x).encode('ascii', 'ignore').decode(
                            'ascii').strip() if x else "<MISSING>" for x in store]

                        # print("data = " + str(store))
                        # print(
                        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store
                        i += 1

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coord = search.next_coord()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
