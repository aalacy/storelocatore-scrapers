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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "raw_address"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "https://www.greatkhans.com"
    r = requests.get("http://www.greatkhans.com/menu", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<INACCESSIBLE>"
    city = "<INACCESSIBLE>"
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "greatkhans"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("data ====== "+str(soup))
    for script in soup.find_all("div", {"class": "menu-item"})[1:]:
        list_location = list(script.stripped_strings)

        location_name = list_location[0]
        raw_address = list_location[1].replace(',', "")[:-9]
        country_code = "US"
        zipp = list_location[1].replace(',', "").split(" ")[-1]
        state = list_location[1].replace(',', "").split(" ")[-2]
        # print("list_location ===== "+str(list_location))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,raw_address]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
