# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "http://www.kenjomarkets.com/locations.aspx"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    store_name = []
    store_detail = []
    return_main_object = []
    k = soup.find_all('div', {'id': 'content'})
    for i in k:
        lat_lgt = []
        names = i.find_all('strong')
        for name in names:
            store_name.append(name.text)

        adds = i.find_all('a')

        for add in adds:
            if len(add['href'].split('ll=')) == 2 or len(add['href'].split('ll=')) == 3:
                lat_lgt.append(add['href'].split('ll=')[1].split('&')[0])
            else:
                if len(add['href'].split('@')) == 2:
                    lat_lgt.append(', '.join(map(str, (add['href'].split('@')[1].split('z')[0].split(',')[:2]))))
                else:
                    lat_lgt.append("<MISSING>,<MISSING>")

        for index, add in enumerate(adds):
            temp_var = []
            if len(add['href'].split('ll=')) == 2 or len(add['href'].split('ll=')) == 3:
                lat_lgt.append(add['href'].split('ll=')[1].split('&')[0])
            else:
                if len(add['href'].split('@')) == 2:
                    lat_lgt.append(', '.join(map(str, (add['href'].split('@')[1].split('z')[0].split(',')[:2]))))
                else:
                    lat_lgt.append("<MISSING>,<MISSING>")

            temp = list(add.stripped_strings)
            street_address1 = temp[0]
            if len(temp) != 1:
                city1 = temp[1].split(',')[0]
                state_zip = temp[1].split(',')[1].split()
                state1 = state_zip[0]

                if len(state_zip) == 2:
                    zipcode1 = state_zip[1]
                else:
                    zipcode1 = "<MISSING>"

                street_address = street_address1
                city = city1
                state = state1
                zipcode = zipcode1
                country_code = "US"
                store_number = "<MISSING>"
                phone = "<MISSING>"
                location_type = "<MISSING>"
                latitude = lat_lgt[index].split(',')[0]
                longitude = lat_lgt[index].split(',')[1]
                hours_of_operation = "<MISSING>"

                temp_var.append(street_address)
                temp_var.append(city)
                temp_var.append(state)
                temp_var.append(zipcode)
                temp_var.append(country_code)
                temp_var.append(store_number)
                temp_var.append(phone)
                temp_var.append(location_type)
                temp_var.append(latitude)
                temp_var.append(longitude)
                temp_var.append(hours_of_operation)
                store_detail.append(temp_var)

    for i in range(len(store_name)):
        store = list()
        store.append("http://www.kenjomarkets.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
