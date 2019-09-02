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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # print("soup ===  first")

    base_url = "https://global.tommy.com"
    r = requests.get("http://global.tommy.com/int/en/stores?storecountry=United+States", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

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
    location_type = "global_tommy"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("soup ==== " + str(soup))

    for script in soup.find_all('div', {'class': 'store-info'}):
        list_address = list(script.stripped_strings)

        city = script.find("dd", {"class": "location"}).text.split(",")[0]
        country_code = "US"
        street_address = script.find("dd", {"class": "street"}).text
        phone = script.find("dd", {"class": "phone"}).text
        hours_of_operation = script.find("dd", {"class": "hours"}).text

        if city is None or len(city) == 0:
            city = "<MISSING>"

        if street_address is None or len(street_address) == 0:
            street_address = "<MISSING>"

        if phone is None or len(phone) == 0:
            phone = "<MISSING>"

        if hours_of_operation is None or len(hours_of_operation) == 0:
            hours_of_operation = "<MISSING>"

        location_name = city
        # print("location ===== "+str(script.find("dd",{"class":"location"}).text))
        # print("street ===== "+str(script.find("dd",{"class":"street"}).text))
        # print("phone ===== "+str(script.find("dd",{"class":"phone"}).text))
        # print("hours ===== "+str(script.find("dd",{"class":"hours"}).text))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
