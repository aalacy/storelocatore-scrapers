import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://mandarinexpress.us"
    r = session.get(base_url + '/locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # for parts in soup.find_all("div", {"class": "rte-content colored-links"}):
    parts = soup.find("div", {"class": "foodmenu"})

    for semi_parts in parts.find_all("p"):
        temp_storeaddresss = list(semi_parts.stripped_strings)
        if(len(temp_storeaddresss) != 1):
            if (len(temp_storeaddresss) == 3):
                location_name = temp_storeaddresss[0]
                street_address = temp_storeaddresss[1]
                city = temp_storeaddresss[2].split(',')[0]
                state_zip = temp_storeaddresss[2].split(',')[1]
                state = state_zip.split(' ')[1]
                store_zip = state_zip.split(' ')[2]
                phone = "<MISSING>"
            if(len(temp_storeaddresss) == 4):
                if(len(temp_storeaddresss[-1]) == 14):
                    location_name = temp_storeaddresss[0]
                    street_address = temp_storeaddresss[1]
                    city = temp_storeaddresss[2].split(',')[0]
                    state_zip = temp_storeaddresss[2].split(',')[1]
                    state = state_zip.split(' ')[1]
                    store_zip = state_zip.split(' ')[2]
                    phone = temp_storeaddresss[-1]
                else:
                    location_name = temp_storeaddresss[0]
                    street_address = temp_storeaddresss[1] + ' ' + temp_storeaddresss[2]
                    city = temp_storeaddresss[3].split(',')[0]
                    state_zip = temp_storeaddresss[3].split(',')[1]
                    state = state_zip.split(' ')[1]
                    store_zip = state_zip.split(' ')[2]
                    phone ="<MISSING>"
            if (len(temp_storeaddresss) == 5):
                location_name = temp_storeaddresss[0]
                street_address = temp_storeaddresss[1]+' '+temp_storeaddresss[2]
                city = temp_storeaddresss[3].split(',')[0]
                state_zip = temp_storeaddresss[3].split(',')[1]
                state = state_zip.split(' ')[1]
                store_zip = state_zip.split(' ')[2]
                phone = temp_storeaddresss[-1]

            return_object = []
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append(phone)
            return_object.append("Mandarin Express")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_main_object.append(return_object)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()


