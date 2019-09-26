import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import sgzip


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():

    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }

    # it will used in store data.
    locator_domain = "http://www.bigdoil.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "bigdoil"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    r = requests.get('http://www.bigdoil.com/locations/', headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    val = soup.find('section', class_="entry")
    for result in val.find_all('div', class_='vc_col-sm-4'):
        for p in result.find_all('p'):
            list_p = list(p.stripped_strings)

            for i in list_p:
                city_state = i.split(',')[-1]
                if ("Cheyenne WY" in city_state and "Big D – 2029 Dell Range Blvd" != i.split(',')[0]) or "Casper WY" in city_state or "Loveland CO" in city_state or "Fort Collins CO" in city_state or "Greeley CO" in city_state or "Big D – 2901 E Grand Ave, Laramie WY" == i or "600 Vandehei Ave" in i:
                    # print(i)
                    list_i = "".join(i.split(',')[0])
                    street_address = list_i.split(
                        '–')[-1].replace('\xa0', "").strip()
                    # print(street_address)
                    cs = "".join(i.split(',')[-1]).split()
                    if len(cs) == 2:
                        city = "".join(cs[0])
                        state = "".join(cs[-1])
                    else:
                        city = " ".join(cs[:2])
                        state = "".join(cs[-1])
                    # print(city + "." + state)
                    location_name = list_i.split('–')[0] + " - " + city
                    phone = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    zipp = "<MISSING>"
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation]
                    store = ["<MISSING>" if x == "" else x for x in store]

                    print("data = " + str(store))
                    print(
                        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    return_main_object.append(store)
            for a in p.find_all('a'):
                # print(a['href'])
                r_loc = requests.get(a['href'], headers=headers)
                soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                # print(soup_loc.prettify())

                for address in soup_loc.find('section', class_="entry").find_all("div", 'wpb_text_column wpb_content_element'):
                    list_add = list(address.stripped_strings)
                    if list_add != []:
                        # print(list_add)
                        # print(len(list_add))
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        if len(list_add) == 2 and "Under 10 Minutes or Less" != list_add[0] and "Full Service Oil Change:" != list_add[0] and "Available Services:" != list_add[0]:
                            street_address = "".join(list_add[0])
                            city = " ".join(list_add[1].split()[:-2])
                            state = "".join(list_add[1].split()[-2])
                            zipp = "".join(list_add[1].split()[-1])
                            location_name = "Big D - " + city
                        elif len(list_add) == 3:
                            street_address = "".join(list_add[1])
                            city = "".join(list_add[2].split()[:-2])
                            state = "".join(list_add[2].split()[-2])
                            zipp = "".join(list_add[2].split()[-1])
                            location_name = "Big D Kwik Shop - " + city

                        elif len(list_add) == 1:
                            street_address = "".join(list_add).split(',')[0]

                            c1 = "".join(list_add).split(',')[1].split()[:-1]
                            city = " ".join(c1)
                            state = "".join(list_add).split(',')[1].split()[-1]
                            zipp = "<MISSING>"
                            location_name = "Big D - " + city
                            # print(city+","+ state+","+location_name)
                        elif "No appointment necessary! We’ll work while you wait!" == list_add[0]:
                            # print(list_add)
                            address = list_add[1].split('services')
                            street_address = address[1].split(
                                'at')[-1].split('in')[0].strip()
                            city = address[1].split(
                                'at')[-1].split('in')[-1].split(',')[0].strip()
                            state = address[1].split(
                                'at')[-1].split('in')[-1].split(',')[-1].replace('.', "").strip()
                            zipp = "<MISSING>"
                            location_name = "".join(address[0]) + " - " + city
                            hours_of_operation = " ".join(list_add[-2:])
                            # print(hours_of_operation)

                        else:

                            if 'Business Hours' == list_add[0]:
                                hours_of_operation = " ".join(list_add).split(
                                    'Amenities')[0].split('Business Hours')[-1].strip()
                            else:
                                hours_of_operation = "<MISSING>"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]
                store = ["<MISSING>" if x == "" else x for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                print("data = " + str(store))
                print(
                    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
    return return_main_object

    # list_p = list(p.stripped_strings)
    #             for i in list_p:
    #                 if 'South Dakota' != i and 'Wyoming' != i and 'Colorado' != i:
    #                     # print(i)
    #                     list_i = "".join(i.split(',')[0])
    #                     street_address = list_i.split('–')[-1]
    #                     cs = "".join(i.split(',')[-1]).split()
    #                     if len(cs) == 2:
    #                         city = "".join(cs[0])
    #                         state = "".join(cs[-1])
    #                     else:
    #                         city = " ".join(cs[:2])
    #                         state = "".join(cs[-1])
    #                     location_name = list_i.split('–')[0] + "," + city
    #                     hours_of_operation = "<MISSING>"
    #                     zipp = "<MISSING>"


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
