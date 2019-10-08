import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://cristinasmex.com"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    parts = soup.find("li", {"class": "dropdown"})
    for semi_parts in parts.find_all("ul", {"class": "dropdown-menu"}):
        for semi_in_parts in parts.find_all("li"):
            store_request = requests.get(base_url + semi_in_parts.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            for inner_part in store_soup.find_all("div", {"id": "course-contact"}):
                temp_storeaddresss = list(inner_part.stripped_strings)
                return_object = []
                hour = temp_storeaddresss[1] +" "+temp_storeaddresss[2]
                street_address = temp_storeaddresss[4]
                city_state = temp_storeaddresss[5]
                city = city_state.split(",")[0]
                state_zip = city_state.split(",")[1]
                state = state_zip.split(" ")[1]
                store_zip = state_zip.split(" ")[2]
                phone= temp_storeaddresss[6]
                location_name= temp_storeaddresss[7]
                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(store_zip)
                return_object.append("US")
                return_object.append("<MISSING>")
                return_object.append(phone)
                return_object.append("Cristinas Mex")
                return_object.append("<MISSING>")
                return_object.append("<MISSING>")
                return_object.append(hour)
                return_main_object.append(return_object)
             
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
