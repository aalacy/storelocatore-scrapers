import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
        'accept': 'application/json'
    }

    # print("soup ===  first")
    addresses = []
    base_url = "https://www.microsoft.com"

    r = session.get("https://www.microsoft.com/en-us/store/locations/find-a-store", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "microsoft"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""

    # print("soup ==== " + str(soup))

    total_result = 0
    page_result = 0
    current_offset = 0
    isFinish = False

    for script in soup.find_all("a", {"class": re.compile("mscom-link")}):

        if "/en-us/store/locations" in script['href'] and script['href'][0] == "/":
            location_url = base_url + script["href"]
            # print("Location URL === " + str(location_url))

            r_location = session.get(location_url, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")

            full_address = ",".join(list(soup_location.find("div",{"class":re.compile("store-address")}).stripped_strings)).replace("Â\xa0","").replace(",,,",",")

            street_address = ", ".join(full_address.split(",")[:-3])
            city = full_address.split(",")[-3]
            state = full_address.split(",")[-2]
            zipp = full_address.split(",")[-1]
            location_name = soup_location.find("div",{"class":re.compile("inner-store-name")}).text
            phone = soup_location.find("div",{"itemprop":"telephone"}).text
            hours_of_operation = " ".join(list(soup_location.find("div",{"class":re.compile("store-hours-wrapper")}).stripped_strings))

            country_code = "US"
            if len(zipp.split(" ")) > 1:
                country_code = "CA"

            # print("hours_of_operation === "+ str(hours_of_operation))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]
            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
            # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
