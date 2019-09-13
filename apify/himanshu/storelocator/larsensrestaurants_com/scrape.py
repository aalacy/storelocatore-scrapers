import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w')as output_file:
        writer = csv.writer(output_file, delimiter=',')
        # header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # body
        for row in data or []:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://larsensrestaurants.com/"
    r = requests.get(
        "https://larsensrestaurants.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []

    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "larsensrestaurants"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for val in soup.find('div', class_="col-xs-12t").find_all('a'):
        # print(val['href'])

        location_name = val.text
        r_loc = requests.get(val['href'], headers=headers)
        s_loc = BeautifulSoup(r_loc.text, "lxml")
        # print(s_loc.prettify())

        info = s_loc.find('div', class_="larsens-locations")
        details = info.find('ul', class_="restaurant_location_details")
        if details is not None:
            address_phone = details.find_all("li")[0]
            list_ap = list(address_phone.stripped_strings)
            # print(len(list_ap))
            # print(list_ap)
            if len(list_ap) == 2:
                state = "".join(list_ap[0].strip().split(',')[-1].split()[0])
                zipp = "".join(list_ap[0].strip().split(',')[-1].split()[-1])
                city = " ".join(list_ap[0].strip().split(',')[0].split("#")[1].split()[-2:])
                street1 = list_ap[0].split(',')[0].split("#")[0]
                street2 = list_ap[0].split(',')[0].split("#")[1].split()[0]
                street_address = street1 + "#"+street2
                phone = "".join(list_ap[1])
            if len(list_ap) == 3:
                street_address = "".join(list_ap[0].strip())
                city = "".join(list_ap[1].split(",")[0].strip())
                state = "".join(list_ap[1].split(",")[1].split()[0].strip())
                zipp = "".join(list_ap[1].split(",")[1].split()[1].strip())
                phone = "".join(list_ap[2].strip())
                # print(street_address, city, state, zipp, phone)
            if len(list_ap) == 4:
                street_address = "".join(list_ap[1].strip())
                city = "".join(list_ap[2].split(',')[0].strip())
                state = "".join(list_ap[2].split(',')[1].split()[0].strip())
                zipp = "".join(list_ap[2].split(',')[1].split()[1].strip())
                phone = "".join(list_ap[0].strip())
            hours = details.find_all("li")[1]
            h1 = "".join(hours.text.strip().replace('\xa0', "").replace(
                "\n", "$").split("$"))
            hours_of_operation = " ".join(h1.split("Reservations Recommended")[0].split('Hours'))

        else:
            details = info.find('div', class_="col-lg-3 col-md-3 col-sm-4 col-xs-12")
            list_details = list(details.stripped_strings)
            if len(list_details) == 11:
                street_address = "".join(list_details[0].strip())
                city = "".join(list_details[1].split(",")[0].strip())
                state = "".join(list_details[1].split(",")[1].split()[0].strip())
                zipp = "".join(list_details[1].split(",")[1].split()[1].strip())
                phone = "".join(list_details[2].strip())
                hours_of_operation = " ".join(list_details[4:9])
                # print(street_address, city, state, zipp, phone, hours_of_operation)
            if len(list_details) == 10:
                street1 = "".join(list_details[1].strip())
                street2 = "".join(list_details[2].split(',')[0].strip())
                street_address = street1+" "+street2
                city = "".join(list_details[2].split(',')[1].strip())
                state = "".join(list_details[2].split(',')[-1].split()[0].strip())
                zipp = "".join(list_details[2].split(',')[-1].split()[-1].strip())
                phone = "".join(list_details[3].strip())
                hours_of_operation = " ".join(list_details[4:-1])
            # print(street_address+" \ "+city+" \ "+state+" \ " +
            #       zipp+" \ " + phone + " \ "+hours_of_operation)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        store = ["<MISSING>" if x == "" else x for x in store]
        return_main_object.append(store)
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
