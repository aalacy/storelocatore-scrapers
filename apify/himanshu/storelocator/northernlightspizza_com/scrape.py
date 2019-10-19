import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
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
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.northernlightspizza.com/"
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



    r= requests.get('https://www.northernlightspizza.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'html.parser')
    zip = soup.find_all('div',class_='row flex-container')[-1].find_all('div',class_='col-xl-2')[0:2]


    script = soup.find_all('script')[-7]
    script_text = script.text.split('var wpgmaps_localize_marker_data = ')[-1].split(';')[0]
    json_data = eval(script_text)
    for x in json_data['2']:
        # print(json_data['2'][x])
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~`')
        location_name = json_data['2'][x]['title']
        street_address = json_data['2'][x]['address'].split(',')[0]

        city =  json_data['2'][x]['address'].split(',')[1]
        state_zipp = json_data['2'][x]['address'].split(',')[2].split()
        if len(state_zipp) ==2:
            state = json_data['2'][x]['address'].split(',')[2].split()[0]
            zipp = json_data['2'][x]['address'].split(',')[2].split()[-1]
        else:
            state = "".join(state_zipp)
            zipp ="<MISSING>"
        latitude = json_data['2'][x]['lat']
        longitude = json_data['2'][x]['lng']
        other = json_data['2'][x]['desc'].split('\n')
        # print(other)
        # print('~~~~~~~~~~~~~~~~~')
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), " ".join(other))
        phone = phone_list[0]
        if len(other)  > 3:
            hours_of_operation = " ".join(other[2:])
            # print(hours_of_operation)
        else:
            hours_of_operation = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]
        print(street_address +"   |  "+ hours_of_operation)

        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)



        # print(zipp)
    for x in json_data['3']:
        # print(json_data['3'][x])
        # print('~~~~~~~~~~~~~~')
        location_name = json_data['3'][x]['title']
        street_address = address = json_data['3'][x]['address'].split(',')[0]
        city = json_data['3'][x]['address'].split(',')[1]
        state_zipp =  json_data['3'][x]['address'].split(',')[2].split()
        if len(state_zipp) ==2:
            state = json_data['3'][x]['address'].split(',')[2].split()[0]
            zipp = json_data['3'][x]['address'].split(',')[2].split()[-1]
            # print(street_address,zipp)
        else:
            state = "".join(state_zipp)
            zipp = "<MISSING>"
        latitude = json_data['3'][x]['lat']
        longitude = json_data['3'][x]['lng']
        other = json_data['3'][x]['desc'].split('\n')
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), " ".join(other))
        phone = phone_list[0]

        if len(other) >3:
             hours_of_operation = " ".join(other[2:])
        else:
            hours_of_operation = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]

        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
