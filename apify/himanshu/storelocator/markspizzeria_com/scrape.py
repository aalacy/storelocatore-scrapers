import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []

    base_url = "https://www.markspizzeria.com"
    r = requests.get("https://www.markspizzeria.com/locations/all", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "markspizzeria"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find('ul', {'class': 'list-group'}).find_all('li'):
        store_url = base_url + script.find('a')['href']
        r_store = requests.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")
        # print('Store URL = ' + store_url)

        list_store_address = list(soup_store.find('div', {'class': 'col-10 postal-address'}).stripped_strings)
        street_address = list_store_address[0]
        city = list_store_address[1]
        location_name = list_store_address[1]
        state = list_store_address[2]
        zipp = list_store_address[3]

        map_location = soup_store.find('div', {'class': 'col-10 postal-address'}).find('a')['href']
        latitude = map_location.split("/@")[1].split(",")[0]
        longitude = map_location.split("/@")[1].split(",")[1]

        phone = str(soup_store.find('div', {'id': 'location-phone'}).find('a', {'href': re.compile('tel:')}).text)
        if 'Coming Soon' in phone:
            phone = '<MISSING>'
            continue

        hours_of_operation = ''.join(list(soup_store.find('div', {'id': 'location-hours-collapse'}).stripped_strings))
        hours_of_operation = hours_of_operation.replace("pm", 'pm,')
        country_code = 'US'

        if hours_of_operation == ":-":
            hours_of_operation = "<MISSING>"

        # print('list_store_address = ' + str(list_store_address))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
