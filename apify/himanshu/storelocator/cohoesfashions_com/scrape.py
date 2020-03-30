import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

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

    base_url = "http://cohoesfashions.com"
    r = session.get(base_url+ "/pg_stores.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("td", {"class": "small"}):
        if(parts.find("div", {"class": "smallbold"})):
            temp_storeaddresss = list(parts.stripped_strings)
            location_name = temp_storeaddresss[0]
            if(len(temp_storeaddresss) == 8 ):
                street_address = temp_storeaddresss[1] + " "+ temp_storeaddresss[2]
                city_state = temp_storeaddresss[3]
                phone = temp_storeaddresss[4]
            else:
                street_address = temp_storeaddresss[1] + " " + temp_storeaddresss[2]+ " " + temp_storeaddresss[3]
                city_state = temp_storeaddresss[4]
                phone = temp_storeaddresss[5]
            city = city_state.split(",")[0]
            state_zip = city_state.split(",")[1]
            state = state_zip.split(" ")[1]
            store_zip = state_zip.split(" ")[2]
            hour = temp_storeaddresss[-2] + " "+ temp_storeaddresss[-1]
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
            return_object.append("micelis")
            return_object.append("<MISSING>")
            return_object.append("<MISSING>")
            return_object.append(hour)
            return_main_object.append(return_object)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
