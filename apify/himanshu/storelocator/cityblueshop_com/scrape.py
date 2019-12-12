import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.cityblueshop.com/"
    r = requests.get(base_url + '/pages/locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("div", {"class": "rte-content colored-links"}):
        for semi_parts in parts.find_all("h3"):
            # print(semi_parts.find("a")['href'])
            store_request = requests.get(semi_parts.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            for inner_parts in store_soup.find_all("div", {"class": "rte-content colored-links"}):
                return_object = []
                locator_domain = "https://www.cityblueshop.com/"
                page_url = semi_parts.find("a")['href']
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                temp_storeaddresss = list(inner_parts.stripped_strings)
                location_name = semi_parts.text
                longitude = inner_parts.find(
                    'iframe')['src'].split('!2d')[-1].split('!')[0].strip()
                latitude = inner_parts.find(
                    'iframe')['src'].split('!3d')[-1].split('!')[0].strip()
                # print(latitude, longitude)
                # print('~~~~~~~~~~~~~~~~`')
                age_index = [i for i, s in enumerate(temp_storeaddresss) if len(
                    s) == 12 and s.replace("-", "").isdigit()]
               # print("=>"+str(age_index))
                no = str(age_index)

                if (len(age_index) == 0):
                    raw_address = temp_storeaddresss[0] + \
                        " " + temp_storeaddresss[1]
                    street_address = " ".join(raw_address.split(',')[
                                              0].split()[:-1]).strip()
                    city = raw_address.split(',')[0].split()[-1].strip()
                    state = raw_address.split(',')[-1].split()[0].strip()
                    zipp = raw_address.split(',')[-1].split()[-1].strip()
                    # print(street_address + " | " + city +
                    #       "  | " + state + "  | " + zipp)

                    phone = temp_storeaddresss[2].split(":")[1]
                    hours_of_operation = temp_storeaddresss[3] + " " + \
                        temp_storeaddresss[4] + " " + temp_storeaddresss[5]
                else:
                    lst = temp_storeaddresss[:age_index[0]]
                    raw_address = " ".join(lst).split(',')
                    raw_address = [el.replace('\xa0', ' ')
                                   for el in raw_address]
                    if len(raw_address) == 1:
                        street_address = " ".join(
                            raw_address[0].split()[:-3]).strip()
                        city = raw_address[0].split()[-3].strip()
                        state = raw_address[0].split()[-2].strip()
                        zipp = raw_address[0].split()[-1].strip()
                    elif len(raw_address) == 2:
                        street_address = " ".join(" ".join(raw_address).split()[
                                                  :-3]).replace("East", "").strip()
                        city = " ".join(" ".join(raw_address).split()[
                            -4:-2]).replace('410', '').replace('Rd', '').strip()
                        state = re.findall(
                            r' ([A-Z]{2}) ', str(" ".join(raw_address)))[-1]
                        zipp = re.findall(re.compile(
                            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(raw_address)))[-1]
                    elif len(raw_address) == 3:
                        street_address = raw_address[0].strip()
                        city = raw_address[-2].strip()
                        state = raw_address[-1].split()[0].strip()
                        zipp = raw_address[-1].split()[-1].strip()
                    elif len(raw_address) == 4:
                        street_address = " ".join(raw_address[:2]).strip()
                        city = raw_address[-2].strip()
                        state = raw_address[-1].split()[0].strip()
                        zipp = raw_address[-1].split()[-1].strip()
                        # print(street_address + " | " + city +
                        #       "  | " + state + "  | " + zipp)
                    else:
                        pass
                        # print(raw_address)
                        # print(len(raw_address))
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    phone = temp_storeaddresss[age_index[0]]
                    hour_list = temp_storeaddresss[age_index[0]:]
                    hours_of_operation = " ".join(
                        " ".join(hour_list).split()[1:]).strip()
                if "NJ" == zipp:
                    zipp = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[1]) + str(store[2]) not in addresses and country_code:
                    addresses.append(str(store[1]) + str(store[2]))
                    store = [el.replace('\xa0', ' ')
                             for el in store]
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
