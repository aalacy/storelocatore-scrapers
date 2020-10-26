import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://pizzanine.com"

    return_main_object = []
    addresses = []
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
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get(
        "https://api.storepoint.co/v1/15acd219ce19bf/locations?rq", headers=headers)

    json_data = r.json()
    # print(json_data['results']['locations'])
    for x in json_data['results']['locations']:

        location_name = x['name']
        address = x['streetaddress'].split(',')
        # print(len(address))
        # print(address)
        if len(address) == 2:
            # print(len(address))
            # print(address)
            street_address = " ".join(
                x['streetaddress'].split(',')[0].split()[:-1])
            city = "".join(x['streetaddress'].split(',')[0].split()[-1])
            state_zipp = x['streetaddress'].split(',')[-1].split()
            if len(state_zipp) == 1:
                state = "".join(state_zipp)
                zipp = "<MISSING>"
            else:
                state = "".join(state_zipp[0])
                zipp = "".join(state_zipp[-1])
            # print(state, zipp)
        elif len(address) == 3:
            # print(len(address))
            # print(address)
            street_address = "".join(address[0])
            city = "".join(address[1])
            state_zipp = address[-1].split()
            # print(state_zipp)
            # print(len(state_zipp))
            if len(state_zipp) == 1:
                state = "".join(state_zipp)
                zipp = "<MISSING>"
            else:
                state = "".join(state_zipp[0])
                zipp = "".join(state_zipp[-1])
            # print(state, zipp)
        else:
            # print(len(address))
            # print(address)
            street_address = " ".join(address[:-2])
            city = "".join(address[-2])
            state = "".join(address[-1])
            zipp = "<MISSING>"
            # print(street_address, city, state, zipp)
        if x['phone'] is not None:
            phone = x['phone']
            # print(phone)
        else:
            phone = "<MISSING>"
        if x['loc_lat'] is not None:
            latitude = x['loc_lat']
            # print(latitude)
        else:
            longitude = "<MISSING>"
        if x['loc_long'] is not None:
            longitude = x['loc_long']
            # print(longitude)
        else:
            longitude = "<MISSING>"
        hours_of_operation = f'monday: {x["monday"]}' + "   " + f'tuesday: {x["tuesday"]}' + "  " + f'wednesday: {x["wednesday"]}' + "  " + \
            f'thursday: {x["thursday"]}' + "    " + f'friday: {x["friday"]}' + \
            "   " + f'saturday: {x["saturday"]}' + \
            "    " + f'sunday: {x["sunday"]}'
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        print("data = " + str(store))
        print(
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
