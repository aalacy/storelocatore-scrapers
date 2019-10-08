import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


countries = {}


def getcountrygeo():
    data = requests.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))


def getplace(lat, lon):
    point = Point(float(lon), float(lat))
    for country, geom in countries.items():
        if geom.contains(point):
            return country

    return "unknown"


def fetch_data():
    getcountrygeo()  # it is use to get country from lat longitude

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    base_url = "http://www.verawang.com"

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
    page_url = "https://www.verawang.com/wp-admin/admin-ajax.php/"

    r = requests.post(page_url, headers=headers,
                      data="action=load_search_results&query=&type%5B%5D=13&type%5B%5D=14&type%5B%5D=15&type%5B%5D=16&type%5B%5D=57")
    json_data = r.json()
    # print("rtext === " + str(json_data))
    soup = BeautifulSoup(json_data["locations"], "lxml")

    for script in soup.find_all("div", {"data-js": "openInfoBox"}):

        latitude = str(script["data-lat"])
        longitude = str(script["data-lng"])
        store_number = script["data-id"]
        location_name = script.find("h4").text

        country_name = getplace(latitude, longitude)
        # print("geo_url === " + str(country_name))
        if "United States of America" != country_name and "Canada" != country_name:
            continue

        address_list = list(script.find("address").stripped_strings)
        # print("address_list ==== " + str(address_list))

        # phone = address_list[-1]
        phone = ""
        zipp = ""
        zip_index = -1
        phone_index = -1
        city = ""
        state = ""

        country_code = "US"
        for str_data in address_list:
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(str_data))
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(str_data))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(str_data))
            state_list = re.findall(r' ([A-Z]{2}) ', str_data)
            if us_zip_list:
                zipp = us_zip_list[-1]
                zip_index = address_list.index(str_data)
                country_code = "US"

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                zip_index = address_list.index(str_data)
                country_code = "CA"

            if state_list:
                state = state_list[-1]

            if phone_list:
                phone = phone_list[0].replace(")", "").replace("(", "")
                phone_index = address_list.index(str_data)

        # print("zipp ==== " + str(zipp))

        if zip_index >= 0:
            # print(str(len(address_list[zip_index - 1].split(","))) + " == zip_index === " + str( address_list[zip_index - 1]))
            if len(address_list[zip_index - 1].split(",")) > 1:
                city = address_list[zip_index - 1].split(",")[0]
                if not zipp:
                    state = address_list[zip_index - 1].split(",")[-1]
                street_address = " ".join(address_list[:zip_index - 1])
            else:
                street_address = " ".join(address_list[:zip_index])
                city = address_list[zip_index].split(",")[0]
        else:
            if phone_index >= 0:
                # print("phone_index === " + str(address_list[phone_index - 1]))
                if len(address_list[phone_index - 1].split(",")) > 1:
                    city = address_list[phone_index - 1].split(",")[0]
                    if not zipp:
                        state = address_list[phone_index - 1].split(",")[-1]
                    street_address = " ".join(address_list[:phone_index - 1])
                else:
                    street_address = " ".join(address_list[:phone_index])
                    city = address_list[phone_index].split(",")[0]

        if "New York" == city:
            state = city

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
