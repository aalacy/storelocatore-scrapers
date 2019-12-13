# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.speedway.com/"

    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        # print(search.current_zip)
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        data = "SearchType=search&SearchText="+str(search.current_zip)+"&StartIndex=0&Limit=10&Latitude="+str(lat)+"&Longitude="+str(lng)+"&Radius=5000&Filters%5BFuelType%5D=Unleaded&Filters%5BOnlyFavorites%5D=false&Filters%5BText%5D="

        location_url ="https://www.speedway.com/Locations/Search"
        try:
            r = requests.post(location_url, headers=headers, data=data)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        data = soup.find_all("div",{"class":"c-location-heading__primary"})
        for i in data:
            href = "https://www.speedway.com"+str(i.find("a")['href'])
            r1 = requests.get(href,headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            info = soup1.find("div",{"class":"cell small-12 large-6"})
            coordinates = soup1.find_all("script")[6].text
            latitude = coordinates.split('lat:')[1].split(',')[0]
            longitude = coordinates.split('lat:')[1].split(',')[1].split('lon:')[1]
            current_results_len = len(info)
            t = list(info.stripped_strings)
            street_address = t[0]
            city = t[2].split(',')[0]
            state = t[2].split(',')[1].split(' ')[1]
            zipp = t[2].split(',')[1].split(' ')[2]
            store_number = t[3].split('#')[1]
            phone = t[4]
            hours = soup1.find("div",{"class":"c-location-options--amenities"})
            if hours != None and hours != []:
                t1 = list(hours.stripped_strings)
                if t1[1] == "Open 24 Hours":
                    hours_of_operation = t1[1]
                else:
                    hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = "<MISSING>"
            result_coords.append((latitude, longitude))
            store = []
            store.append(base_url)
            store.append("<MISSING>")
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number) 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(href)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
