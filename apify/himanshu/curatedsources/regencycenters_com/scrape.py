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
    base_url = "http://regencycenters.com/"
    r = requests.get("https://www.regencycenters.com/api/GetCenters", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = json.loads(soup.text)

    for r in data:
        p_data = data[r]
        for p in p_data:
            location_name = p['BusinessUnitName']
            street_address = p['BusinessUnitAddress1'].split(",")[0]
            address = p['BusinessUnitAddress2']
            city = address.split(",")[0]
            state_zip = address.split(",")[1]
            state = state_zip.split(" ")[1]
            store_zip = state_zip.split(" ")[2]
            store_id = p['BusinessUnitID']
            lat = p['Longitude']
            lag = p['Latitude']
            if (location_name == ''):
                location_name = "<MISSING>"
            if (street_address == ''):
                street_address = "<MISSING>"
            if (city == ''):
                city = "<MISSING>"
            if (state == ''):
                state = "<MISSING>"
            if (store_zip == ''):
                store_zip = "<MISSING>"
            if (store_id == ''):
               store_id = "<MISSING>"
            if (lat == ''):
                lat = "<MISSING>"
            if (lag == ''):
                lag = "<MISSING>"
            phone = "<MISSING>"
            return_object = []
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append(store_id)
            return_object.append(phone)
            return_object.append("Regency centers")
            return_object.append(lat)
            return_object.append(lag)
            return_object.append("<MISSING>")
            return_main_object.append(return_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
