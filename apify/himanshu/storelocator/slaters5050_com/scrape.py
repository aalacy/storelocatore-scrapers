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
    base_url = "https://slaters5050.com"
    r = requests.get("https://slaters5050.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    addresses = []
    for location in soup.find_all("li", {'class': re.compile("menu-item menu-item-type-post_type menu-item-object-locations")}):
        page_url = location.find("a")["href"]
        location_request = requests.get(
            location.find("a")["href"], headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        name = location_soup.find(
            "main", {'role': "main"}).find("h1").text.strip()
        # print(name)
        address = list(location_soup.find(
            "p", {'class': "address"}).stripped_strings)
        if "Free Valet Parking" in " ".join(address):
            address.remove("Free Valet Parking")
        if len(address) < 4:
            street_address = " ".join(address[:-1]).strip()
            city = address[-1].split(',')[0].strip()
            state = address[-1].split(',')[-1].split()[0].strip()
            zipp = address[-1].split(',')[-1].split()[-1].strip()
        else:
            street_address = address[0]
            city = address[1]
            state = address[2].split()[0].strip()
            zipp = address[2].split()[-1].strip()
        hours = " ".join(list(location_soup.find(
            "div", {'class': "hours"}).stripped_strings)).split('Happy Hour Menu')[0]
        phone = location_soup.find("p", {'class': "phone"}).text.strip()
        store = []
        store.append("https://slaters5050.com")
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(page_url)

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        return_main_object.append(store)
        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
