import csv
import requests
from bs4 import BeautifulSoup, Comment
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    return_main_object = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # it will used in store data.
    locator_domain = "https://ibabc.org/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "ibabc"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    r = requests.get("https://ibabc.org/index.php?option=com_storelocator&view=map&format=raw&searchall=0&Itemid=511&lat=49.2843731&lng=-123.11644030000002&radius=100&catid=-1&tagid=-1&featstate=0&name_search=", headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    for x in soup.find_all("marker"):
        location_name = x.find("name").text
        latitude = x.find('lat').text
        longitude = x.find("lng").text

        if "-" == x.find('phone').text:
            phone = "<MISSING>"
        else:
            phone = x.find('phone').text
        address = x.find('address')
        address_list = list(address)
        # print(address_list)
        street_address = "".join(address_list).split(',')[0]
        # print(street_address)
        # print("".join(address_list).split(',')[1].split())
        # print(len("".join(address_list).split(',')[1].split()) )
        c_list = "".join(address_list).split(',')[1].split()
        if len(c_list) == 1:
            city = "".join(c_list)
        if len(c_list) == 2 and ("BC" != c_list[-1] and "0B5" != c_list[-1]):
            city = " ".join(c_list)
            # print(city)
        if len(c_list) == 2 and ("BC" == c_list[-1]):
            city = "".join(c_list[0])
            # print(city)
        if "0B5" == c_list[-1]:
            city = "North Vancouver"

        z = "".join(address_list).split(',')
        # print(z)
        # print(len(z))
        # print("~~~~~~~~~~~~~~~~~~~~")
        if len(z) == 2:
            # print(z)
            # print(len(z))
            # print("~~~~~~~~~~~~~~~~~~~~")
            z1 = z[-1].split()
            # print(len(z1))
            # print(z1)
            if len(z1) == 3:
                zipp = " ".join(z1[1:])
                # print(zipp)
            if len(z1) == 4:
                zipp = " ".join(z1[2:])
                # print(zipp)
            if len(z1) == 5:
                zipp = " ".join(z1[3:])
                # print(zipp)
            if len(z1) == 2:
                # print(address_list)
                zipp = x.find('custom4').text.strip()
                # print(zipp)
                if " " == x.find('custom4').text:
                    zipp = "<MISSING>"
                    # print(zipp)
        if len(z) == 3:
            # print(z)
            # print(len(z))
            # print("~~~~~~~~~~~~~~~~~~~~")
            z1 = z[-1].split()
            # print(len(z1))
            # print(z1)
            if len(z1) == 3:
                zipp = " ".join(z1[1:])
                # print(zipp)
            if len(z1) == 2:
                zipp = " ".join(z1)
                # print(zipp)
            if len(z1) == 1:
                zipp = x.find('custom4').text.strip()
                # print(zipp)
                if " " == x.find('custom4').text:
                    zipp = "<MISSING>"
                    # print(zipp)
        if len(z) > 3:
            # print(z)
            # print(len(z))
            # print("~~~~~~~~~~~~~~~~~~~~")
            z1 = z[-1].split()
            # print(len(z1))
            # print(z1)
            if len(z1) == 1:
                zipp = x.find('custom4').text.strip()
                # print(zipp)
                if " " == x.find('custom4').text:
                    zipp = "<MISSING>"
                    # print(zipp)
            else:
                zipp = " ".join(z1).strip()
                # print(zipp)
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]
        store = ["<MISSING>" if x == "" else x for x in store]
        print("data = " + str(store))
        print(
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
