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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    for zip_code in zips:
        # print(zip_code)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        base_url = "https://www.bn.com"

        # zip_code = 11030
        r = requests.get("https://stores.barnesandnoble.com/stores?page=0&size=1000000&searchText=" + str(
            zip_code) + "+&storeFilter=all&view=list&v=1", headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        # it will used in store data.
        locator_domain = base_url
        location_name = ""
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "barnesandnoble"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        raw_address = ""
        hours_of_operation = "<MISSING>"

        # print("data ==== "+str(soup))

        for script in soup.find_all("div", {"class": "col-md-7 col-lg-7 col-sm-7 col-xs-7"}):
            # address_list = list(script.stripped_strings)
            location_url = "https://stores.barnesandnoble.com" + script.find('a')['href']
            # print("location_url === " + str(location_url))

            r_location = requests.get(location_url, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")

            address_list = list(
                soup_location.find('div', {'class': 'col-sm-8 col-md-4 col-lg-4 col-xs-6'}).stripped_strings)

            store_hours_index = [i for i, s in enumerate(address_list) if 'Store Hours:' in s]

            scz_index = -1
            for val in address_list:
                if str(val[-5:]).isdigit():
                    scz_index = address_list.index(val)

            # print(str(scz_index) + " ----------- address_list === " + str(address_list))

            location_name = address_list[0]
            hours_of_operation = " ".join(address_list[store_hours_index[0]:-1])

            if scz_index >= 0:
                city = address_list[scz_index].split(',')[0]
                state = address_list[scz_index].split(',')[1].strip().split(' ')[0]
                zipp = address_list[scz_index].split(',')[1].strip().split(' ')[1]
                phone = address_list[scz_index+1][:12]
                street_address = ", ".join(address_list[1:scz_index])
            else:
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                street_address = "<MISSING>"
                phone = '<MISSING>'

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if store[2] in addresses:
                continue

            addresses.append(store[2])

            store = ["<MISSING>" if x == "" else x for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
        # break
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
