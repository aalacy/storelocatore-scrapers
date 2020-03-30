import csv
#import sys
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
    base_url = "https://sportclips.ca/"

    addresses = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ""
    r = session.get(
        "https://sportclips.ca/store-locator")
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find(lambda tag: (
        tag.name == 'script') and "data" in tag.text).text.split(" data = ")[1].split(';')[0].strip()
    json_data = json.loads(script)
    for loc in json_data:
        store_number = loc["id"]
        location_name = loc["SiteName"]
        latitude = loc["lat"]
        longitude = loc["lng"]
        street_address = loc["Address"]
        city = loc["City"]
        state = loc["State"]
        zipp = loc["Postal"]
        country_code = "CA"
        page_url = loc["Web"]
        r_loc = session.get(page_url)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        try:
            info = list(soup_loc.find(
                "div", {"id": "Store_info_wrapper"}).stripped_strings)
            phone_list = re.findall(re.compile(
                ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(info[-1]))
            if phone_list:
                phone = "(" + phone_list[-1].strip()
            else:
                phone = "<MISSING>"
            geo = soup_loc.find("iframe")["src"]
            latitude = geo.split('!2d')[1].split("!2")[0].split("!3d")[0]
            latitude = geo.split('!2d')[1].split("!2")[0].split("!3d")[1]
            hours_of_operation = " ".join(list(soup_loc.find(
                "div", class_="container second").stripped_strings)).split("GET DIRECTIONS")[0].replace("STORE HOURS", "").strip()
        except:
            pass
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[7]) not in addresses:
            addresses.append(str(store[7]))
            store = [x if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
