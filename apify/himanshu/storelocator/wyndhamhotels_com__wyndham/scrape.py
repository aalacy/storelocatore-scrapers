import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.wyndhamhotels.com"
    r = requests.get(
        "https://www.wyndhamhotels.com/en-uk/wyndham/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())

    return_main_object = []
    address2 = []
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
    location_type = "wyndhamhotels"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for val in soup.find_all('div', {'class': 'aem-rendered-content'}):
        # print(val)
        location_name = val.find('div', class_="region").text.strip()
        country = val.find('h4', class_='country-name').text
        # print(country)
        if country == 'United States':

            for address in val.find_all('div', class_='state-container'):
                add1 = address.text.strip()
                # print(add1)
                for li in address.find_all("ul"):
                    link = li.find('a')['href'].split('/')
                    link[5] = 'local-area'
                    main_link = base_url + "/".join(link)
                    # print(main_link)
                    r1 = requests.get(main_link, headers=headers)
                    soup_location = BeautifulSoup(r1.text, "lxml")
                    # print(soup_location)
                    address = soup_location.find(
                        'div', class_="uu-glance-localarea").text
                    add1 = address.strip().replace(
                        '\n\n', '\n').strip().replace('\t', '')
                    add1 = re.sub("[\t ]+", " ", add1).split('\n')
                    if add1[4] == "US":
                        del add1[4]
                        street_address = "".join(add1[0])
                        city = "".join(add1[1])
                        state = "".join(add1[2])
                        zipp = "".join(add1[-1])
                        # print(street_address, city, state, zipp)
                    p = soup_location.find(
                        'div', class_="travel-info").find('div', class_="col-xs-24")
                    if p != None:
                        p1 = p.text.split("\n")
                        # print(p1)
                        del p1[0]
                        del p1[2]
                        # print(p1)
                        phone = "".join(p1[-1])
                        # print(phone)

                    if p == None:
                        phone = "<MISSING>"
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation]

                    store = ["<MISSING>" if x == "" else x for x in store]
                    if store[3] in address2:
                        continue
                    address2.append(store[3])


                    # print('Data == ' + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
