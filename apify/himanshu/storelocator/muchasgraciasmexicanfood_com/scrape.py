import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://muchasgraciasmexicanfood.com"
    r = requests.get(
        "http://muchasgraciasmexicanfood.com/our-locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    for state in soup.find_all("div", {"class": "avaris-pagebuilder-block avaris-pagebuilder-block-column col-sm-6"}):
        state_request = requests.get(state.find("a")["href"], headers=headers)
        state_soup = BeautifulSoup(state_request.text, 'lxml')
        for location in state_soup.find_all("div", {'class': "avaris-pagebuilder"}):
            for link in location.find_all("a"):
                location_request = requests.get(link["href"], headers=headers)
                location_soup = BeautifulSoup(location_request.text, 'lxml')
                for store_data in location_soup.find_all("div", {"class": "avaris-pagebuilder-block"}):
                    location_details = list(store_data.stripped_strings)
                    if len(location_details) > 2 and len(location_details) < 6:
                        if len(location_details) == 4:
                            if location_details[2] in address:
                                continue
                            location_details = location_details[1:]
                            address.append(location_details[1])
                        else:
                            if location_details[1] in address:
                                continue
                            address.append(location_details[1])
                        store = []
                        store.append("http://muchasgraciasmexicanfood.com")
                        store.append(location_details[0])
                        if len(location_details[1].split(",")) == 3:
                            store.append(location_details[1].split(",")[0])
                            store.append(location_details[1].split(",")[1])
                        else:
                            store.append(
                                " ".join(location_details[1].split(",")[0].split(" ")[:-1]))
                            store.append(location_details[1].split(
                                ",")[0].split(" ")[-1])
                        if len(location_details[1].split(",")[-1].split(" ")) < 3:
                            store.append(location_details[1].split(
                                ",")[-1].split(" ")[-1])
                            store.append("<MISSING>")
                        else:
                            store.append(location_details[1].split(
                                ",")[-1].split(" ")[-2])
                            store.append(location_details[1].split(
                                ",")[-1].split(" ")[-1])
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(location_details[2])
                        store.append("<MISSING>")
                        if store_data.find("a", {"href": re.compile("/@")}) == None:
                            try:
                                geo_location = location_soup.find(
                                    "a", {"href": re.compile("/@")})["href"]
                            except:
                                continue
                        else:
                            geo_location = store_data.find(
                                "a", {"href": re.compile("/@")})["href"]
                        store.append(geo_location.split("/@")[1].split(",")[0])
                        store.append(geo_location.split("/@")[1].split(",")[1])
                        store.append("<MISSING>")
                        store.append(link["href"])
                        return_main_object.append(store)
                        # print("data == " + str(store))
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
