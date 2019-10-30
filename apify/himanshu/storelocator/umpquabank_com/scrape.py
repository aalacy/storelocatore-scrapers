import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import calendar

# import time


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []



    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    #     "accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

    # it will used in store data.
    locator_domain = "https://www.umpquabank.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    url = "https://www.umpquabank.com/api/v1/locations"
    for zip_code in zips:
        # print(zip_code)
        try:
            payload = "{\"latitude\":"+str(zip_code[0])+",\"longitude\":"+str(zip_code[1])+",\"atm\":false,\"openNow\":false,\"openSaturdays\":false,\"driveUpWindow\":false,\"date\":\"2019-10-30T06:55:41.071Z\"}"
            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache",
                'postman-token': "9f11fe08-b1d3-728a-cd1b-ff35b517f92b"
                }

            response = requests.request("POST", url, data=payload, headers=headers)
            json_data = response.json()

        except:
            continue
        # print(json_data)
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        for loc in json_data['locations']:
            store_number = loc['storeNumber']
            if loc['addressLine2'] != None:
                street_address = loc['addressLine1'] +" " +loc['addressLine2']
            else:
                street_address  = loc['addressLine1']
            city = loc['city']
            state = loc['state']
            zipp = loc['zip']
           # print(zipp)
            phone = loc['phoneNumber']
            latitude = loc['latitude']
            longitude = loc['longitude']
            location_name = city
            h = []
            for hours in loc['hours']:
                if hours['openHour'] == None and hours['closedHour'] == None:
                    hr = "Closed"
                    h.append(hr)

                else:
                    hr = hours['openHour'] +" - "+ hours['closedHour']
                    h.append(hr)
            hour = ",".join(h).split(',')
            hour.insert(0,'Sun')
            hour.insert(2,'Mon')
            hour.insert(4,'Tue')
            hour.insert(6,'Wed')
            hour.insert(8,'Thu')
            hour.insert(10,'Fri')
            hour.insert(12,'Sat')

            hours_of_operation = " ".join(hour).strip()

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == "Blank" else x for x in store]
            if store_number in addresses:
                continue
            addresses.append(store_number)

           # print("data = " + str(store))
          

            return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
