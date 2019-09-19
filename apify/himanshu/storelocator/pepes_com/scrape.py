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

    base_url = "https://pepes.com"
    r = requests.get(
        "https://pepes.com/locations-pepes-mexican-restaurants-food-chicago.php", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())

    return_main_object = []

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
    location_type = "pepes"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for links in soup.find('div', {'id': 'map'}).find_all('a'):
        link = "https://pepes.com/locations-pepes-mexican-restaurants-food-chicago.php"
        r_location = requests.get(link + links['href'], headers=headers)
        soup_location = BeautifulSoup(r_location.text, 'lxml')
        # print(soup_location.prettify())
        for location_result in soup_location.find('div', {'id': 'location-results'}).find('ul').find_all('a'):
            loc_res = base_url+location_result['href']
            result_location = requests.get(loc_res, headers=headers)
            result_soup = BeautifulSoup(result_location.text, 'lxml')
            # print(result_soup.prettify())
            location_content = result_soup.find(
                'div', {'id': 'location-content'}).find('div', {'id': 'location-desc'})
            location_name = location_content.find('h1').text

            street_address = location_content.find('ul').find('li').text.strip()
            tag_address = location_content.find('ul').find('li').nextSibling
            address = list(tag_address.stripped_strings)
            city = "".join(address[0].split(',')[0])
            state = address[0].split(',')[1].split(' ')[1].strip()
            zipp = address[0].split(',')[1].split(' ')[-1].strip()
            # print(street_address+" \ "+city+" \ "+state+" \ " +
            #       zipp)
            tag_phone = location_content.find('ul').find('li').nextSibling.nextSibling
            ph = list(tag_phone.stripped_strings)
            phone = "".join(ph[0].split(':')[1]).replace('or (219) 769-PEPE','')
            

            hours_content = result_soup.find(
                'div', {'id': 'location-content'}).find('div', {'id': 'location-hours'})
            hours = list(hours_content.stripped_strings)
            hours_of_operation = " ".join(hours)

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
