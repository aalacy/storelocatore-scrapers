import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    cords = sgzip.coords_for_radius(50)
    for cord in cords:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        r = session.get("https://www.quantumvisioncenters.com/wp-json/352inc/v1/locations/coordinates?lat=" + str(cord[0]) + "&lng=" + str(cord[1]),headers=headers)
        if r.text == "null":
            continue
        else:
            data = r.json()
            for store_data in data:
                store = []
                store.append("https://www.quantumvisioncenters.com")
                store.append(store_data["name"])
                store.append(store_data["address1"] + " " + store_data['address2'] + " " + store_data["address3"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zip_code"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["phone_number"] if store_data["phone_number"] != "" and store_data["phone_number"] != None else "<MISSING>")
                store.append("the eye doctors")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                location_request = session.get(store_data["permalink"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                hours = " ".join(list(location_soup.find("div",{"class":"col-lg-4 times"}).stripped_strings))
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
