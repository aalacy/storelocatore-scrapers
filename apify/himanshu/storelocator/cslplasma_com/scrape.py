
import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.cslplasma.com"
    r = requests.get(base_url + "/locations/search-results-state")
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())
    return_main_object = []
    comming_soon = []
    for option in soup.find('select', {"name": "SelectedState"}).find_all("option"):
        if option['value'] == "":
            continue
        location_request = requests.get(base_url + option['value'])
        lcoation_soup = BeautifulSoup(location_request.text, 'lxml')
        # section = soup_loc.find('section', class_='center-search-results')
        # container = soup_loc.find('div', class_='center-search-item-container')

        for location in lcoation_soup.find_all("div", {"class": "center-search-item"}):
            # print(location.prettify())
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            store = []

            location_address = list(location.find(
                "div", {"class": "center-search-item-addr"}).stripped_strings)
            if location_address[1] != "Coming Soon" and location_address[1] != "Coming soon":

                name = location.find(
                    "span", {'class': "center-search-item-name"}).text

                street_address = location_address[1].strip()
                # if "Coming Soon" in street_address:
                #     print(street_address)
                city = location_address[-1].split(',')[0].strip()
                state = location_address[-1].split(',')[-1].split()[0].strip()
                zipp = location_address[-1].split(',')[-1].split()[-1].strip()
                if "" == city:
                    city = "<MISSING>"
                location_hours = list(location.find(
                    'div', {"class": "center-search-item-contact"}).stripped_strings)

                phone = ""
                if "Ph" in location_hours:
                    phone = location_hours[location_hours.index("Ph") + 1]
                    # print(phone)
                page_url = base_url + location.find_all("a")[-1]['href']
                # print(page_url)
                geo_location = location.find('a')['href']
                #print(geo_location)
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                store = []
                store.append("https://www.cslplasma.com")
                store.append(name)
                store.append(street_address)
                store.append(city if city != "" else "<MISSING>")
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone != "" else "<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(location_hours[-1] if location_hours[-1] !=
                             "Contact Info" and location_hours[-1] != "Coming Soon" else "<MISSING>")
                store.append(page_url)
                # print(str(store[2]))
                # print('~~~~~~~~~~~~~~~~~~~~`')
                return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
