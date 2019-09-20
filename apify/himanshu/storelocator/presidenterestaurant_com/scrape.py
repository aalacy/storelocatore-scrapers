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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': 'application/json'
    }

    # print("soup ===  first")
    addresses = []
    base_url = "https://www.presidentebarandgrill.com"

    r = requests.get("https://www.presidentebarandgrill.com/", headers=headers)
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
    location_type = "presidentebarandgrill"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""

    for script in soup.find_all("div", {"class": "wpb_raw_code wpb_content_element wpb_raw_html"}):
        # print("location ==== " + str(script.parent.find("h4").text))

        full_address_url = script.find("iframe")["src"]
        geo_request = requests.get(full_address_url, headers=headers)
        geo_soup = BeautifulSoup(geo_request.text, "lxml")
        for script_geo in geo_soup.find_all("script"):
            if "initEmbed" in script_geo.text:
                geo_data = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]

        # print("geo_data ===== "+ geo_data)
        location_name = geo_data.split(',')[0]
        street_address =geo_data.split(',')[1]
        city =geo_data.split(',')[2]
        state =geo_data.split(',')[-1].strip().split(" ")[0]
        zipp =geo_data.split(',')[-1].strip().split(" ")[-1]
        latitude = lat
        longitude = lng

        phone = "("+ script.parent.find("h4").text.split("(")[1]

        # print("phone === "+ str(phone))

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
