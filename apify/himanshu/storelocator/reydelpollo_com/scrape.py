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
    locator_domain = "https://reydelpollo.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "reydelpollo"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= requests.get('https://reydelpollo.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    for column in soup.find_all('div',class_='vc_col-sm-6'):
        # print(column.prettify())
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        address = column.h4
        if address is not None:
            list_add = list(address.stripped_strings)
            # print(list_add)
            location_name = list_add[0]
            street_address = list_add[-1].split(',')[0]
            city = list_add[-1].split(',')[1]
            state = list_add[-1].split(',')[-1].split()[0]
            zipp = list_add[-1].split(',')[-1].split()[-1]
            hours = soup.find(lambda tag: (
                    tag.name == "p") and "FOOD MENU" == tag.text).nextSibling.nextSibling
            listhours = list(hours.stripped_strings)

            hours_of_operation = " ".join(listhours[1:])
            phone = column.a.text.strip()
        if address is None:

            iframe = column.find('iframe')['src'].split('!2d')[-1].split('!3d')
            longitude = iframe[0]
            latitude = iframe[-1].split('!')[0]


            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')

            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            # print("data===="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            return_main_object.append(store)


    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
