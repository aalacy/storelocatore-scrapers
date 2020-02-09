# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.selectspecialtyhospitals.com/"

    for i in range(0,228):

        if 360 == (8*i):
            continue
        location_url = "https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&v={D2D3D65E-3A18-43DD-890F-1328E992446A}&p=8&e="+str(8*i)
        try:
            r = requests.get(location_url, headers=headers)
            json_data = r.json()
        except:
            continue

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = "<MISSING>"
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        hours_of_operation = "<MISSING>"
        if json_data["Results"] != []:
            for location in json_data["Results"]:                             
                soup = BeautifulSoup(location['Html'], "lxml")
              
                latitude = soup.find("div",{"class":"locations-map"}).find("a")['href'].split('=')[-1].split(',')[0]
                longitude = soup.find("div",{"class":"locations-map"}).find("a")['href'].split('=')[-1].split(',')[1]

            
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
                

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
    
                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))
                    store = [str(x).encode('ascii', 'ignore').decode(
                        'ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
                       

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
