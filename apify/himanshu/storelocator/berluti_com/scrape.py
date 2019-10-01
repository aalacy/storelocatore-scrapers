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



    base_url = "https://www.berluti.com"
    # r = requests.get("http://store.berluti.com/search?country=us", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
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
    location_type = "berluti"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("data ==== "+str(soup))

    r_us = requests.get("http://store.berluti.com/search?country=us", headers=headers)
    soup_us = BeautifulSoup(r_us.text, "lxml")

    for script_us in soup_us.find_all('div',{'class':'container'}):
        address_list = list(script_us.stripped_strings)

        if 'Closed' in address_list:
            # print("script_us === " + str(address_list))
            location_name = address_list[0]
            street_address = address_list[1] +", "+ address_list[2]

            closed_index = [i for i, s in enumerate(address_list) if 'Closed' in s]

            city = address_list[closed_index[0]-3]

            if len(address_list[closed_index[0]-2].split(" ")) > 1:
                zipp = address_list[closed_index[0]-2].split(" ")[1]
                state = address_list[closed_index[0]-2].split(" ")[0]
            else:
                zipp = address_list[closed_index[0]-2]
                state = "<MISSING>"

            phone = address_list[closed_index[0]-1]

            hours_url = "http://store.berluti.com" + script_us.find("a",{"class":"components-outlet-item-search-result-basic__link__details__link"})["href"]
            # print("script_us === " + str(hours_url))
            r_hours = requests.get(hours_url, headers=headers)
            soup_hours = BeautifulSoup(r_hours.text, "lxml")

            hours_of_operation = " ".join(list(soup_hours.find("div",{"class":"components-outlet-item-hours-retail"}).stripped_strings))

            street_address = street_address.replace(city,"")
            # print("hours_of_operationty ====== "+ str(hours_of_operation))

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
