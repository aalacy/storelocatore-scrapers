import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.wingsetc.com"
    r = requests.get(
        'https://www.wingsetc.com/locations/?CallAjax=GetLocations')
    data = r.json()
    addresses = []
    hours_of_operation = "<MISSING>"
    for i in data:
        locator_domain = base_url
        location_name = i['FranchiseLocationName']
        street_address = i['Address1']
        city = i['City']
        state = i['State']
        zipp = i['ZipCode']
        phone = i['Phone']
        latitude = i['Latitude']
        longitude = i['Longitude']
        store_number = i['FranchiseLocationID']
        country_code = "US"
        location_type = "<MISSING>"
        page_url = base_url + i['Path']
        r1 = requests.get(page_url)
        soup1 = BeautifulSoup(r1.text,"lxml")
        #print(page_url)
        try:
            hours_of_operation = " ".join(list(soup1.find("div",{"class":"local-hours ui-repeater"}).stripped_strings)[1:])
        except:
            hours_of_operation  ="<MISSING>"
        # print(" ".join(list(soup1.find("div",{"class":"local-hours ui-repeater"}).stripped_strings)[1:]))
        # # exit()
        # hour = i['LocationHours']
        # if hour != None:
        #     hours = i['LocationHours'].split('[')
        #     hr = []
        #     for h in hours:
        #         if "" != h:
        #             # print(h)
        #             # print('~~~~~~~~~~~~```````~~~~~')

        #             hour_list = "[" + h
        #             hours1 = " ".join(hour_list.split(':')[
        #                 1:-2]).replace(',"OpenTime"', '').replace(',"CloseTime"', '').replace(',"Closed"', '').replace('"', "").split()

        #             hours1.insert(-3, ' - ')
        #             h1 = ":".join(
        #                 hours1).replace(': - :', ' - ').strip()
        #             hr.append(h1)
        #     if hr == []:
        #         hours_of_operation = "<MISSING>"
        #     else:
        #         hours_of_operation = " , ".join(hr)

        # else:
        #     hours_of_operation = "<MISSING>"
        # print(hours_of_operation)
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses and country_code:
            addresses.append(str(store[1]) + str(store[2]))

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
