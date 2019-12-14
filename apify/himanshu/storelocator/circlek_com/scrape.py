import csv
import sys
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.circlek.com"

    addresses = []
    result_coords = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""

    location_url = "https://www.circlek.com/stores_new.php?lat=33.6&lng=-112.12&distance=10000000000000&services=&region=global"
    r = requests.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    k = json.loads(soup.text)['stores']
    for i in k:
        while True:
            try:
                r1 = requests.get(base_url + k[i]['url'], headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                break
            except:
                continue
        # r1 = requests.get(base_url+k[i]['url'], headers=headers)

        location_name1 = '<MISSING>'
        street_address1 = soup1.find("h1", {"class": "heading-big"})
        if street_address1 != None:
            street_address = street_address1.text.replace(
                "\n", "").split(",")[-1].strip()
        else:
            street_address = "<MISSING>"
        zipp1 = soup1.find("h2", {"class": "heading-small"})
        if zipp1 != None:
            zipp = list(zipp1.stripped_strings)[-1]
        else:
            zipp = "<MISSING>"

        if len(zipp) == 6 or len(zipp) == 7:
            country_code = "CA"
        else:
            country_code = "US"

        city1 = soup1.find("h2", {"class": "heading-small"})
        if city1 != None:
            city = list(city1.stripped_strings)[0]
        else:
            city = "<MISSING>"
        state1 = soup1.find("h2", {"class": "heading-small"})
        if state1 != None:
            state2 = re.sub('\s+', ' ', state1.text).split(',')
            if len(state2) != 2:
                state = state2[1]
            else:
                state = "<MISSING>"
        else:
            state = "<MISSING>"
        phone1 = soup1.find("div", {
                            "class": "store-info__item store-info__item--phone icon-circlek_icons_telephone"})
        if phone1 != None:
            phone = phone1.text.replace("\n", "")
        else:
            phone = "<MISSING>"
        if "(5200 868-8097" == phone :
            phone = "<MISSING>"
        hours_of_operation1 = soup1.find(
            "div", {"class": "columns large-12 middle hours-wrapper"})
        if hours_of_operation1 != None:
            hours_of_operation = " ".join(
                list(hours_of_operation1.stripped_strings))
        else:
            hours_of_operation = "<MISSING>"
        latitude = k[i]['latitude']
        longitude = k[i]['longitude']
        page_url = base_url + k[i]['url']
        store = [locator_domain, location_name.encode('ascii', 'ignore').decode('ascii').strip(), street_address.encode('ascii', 'ignore').decode('ascii').strip(), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                 store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitude, hours_of_operation.replace("hours", "").encode('ascii', 'ignore').decode('ascii').strip(), page_url]

        if "<MISSING>" in store[2]:
            pass
        else:
            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))
                store = [x if x else "<MISSING>" for x in store]
                #print("data = " + str(store))
                #print(
                    # '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
