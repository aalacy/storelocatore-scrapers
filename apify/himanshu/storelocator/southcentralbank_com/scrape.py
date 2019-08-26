import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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

    base_url = "https://www.1hotels.com"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "menu menu-level-0"}):
            semi_part = parts.find_all("li", {"class": "menu-item menu-item--expanded"})[0]
            for inner_semi_part in semi_part.find_all("span", {"class": "menu-item col-12 col-md-4 col-lg-3","data-id":"open-2"}):
                if (inner_semi_part.find("a")):
                    store_request = requests.get(base_url + inner_semi_part.find("a")['href'])
                    store_soup = BeautifulSoup(store_request.text, "lxml")
                    temp_iframe = store_soup.find("p",{"class": "directions__address"})
                    find_url = temp_iframe.find("a")['href']
                    str = find_url.split("@")[1]
                    lat = str.split(",")[0]
                    lag = str.split(",")[1]
                    for in_semi_part in store_soup.find_all("section",{"class": "directions"}):
                        return_object = []
                        temp_storeaddresss = list(in_semi_part.stripped_strings)
                        location_name = temp_storeaddresss[1]
                        street_address = temp_storeaddresss[2]
                        city_state = temp_storeaddresss[3]
                        city = city_state.split(",")[0]
                        state_zip = city_state.split(",")[1]
                        state = state_zip.split(" ")[1]
                        store_zip = state_zip.split(" ")[2]
                        return_object.append(base_url)
                        return_object.append(location_name)
                        return_object.append(street_address)
                        return_object.append(city)
                        return_object.append(state)
                        return_object.append(store_zip)
                        return_object.append("US")
                        return_object.append("<MISSING>")
                        return_object.append("<MISSING>")
                        return_object.append("1hotels")
                        return_object.append(lat)
                        return_object.append(lag)
                        return_object.append("<MISSING>")
                        return_main_object.append(return_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
