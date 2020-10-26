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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
       'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = "action=get_properties_for_map"
    base_url = "https://www.stayboarders.com"
    r = session.post("https://www.staycobblestone.com/wp-admin/admin-ajax.php", headers=headers, data = data)
    print(r)
    soup = BeautifulSoup(r.text, "lxml")
    data = json.loads(soup.text)
    for r in data:
        p_data = data[r]['properties']
        for p in p_data:
            in_data = p_data[p]
            if in_data["status"] != "open":
                continue
            location_name = in_data['type']
            if (location_name == ''):
                location_name = "<MISSING>"
            street_address = in_data['address']
            if (street_address == ''):
                street_address = "<MISSING>"
            city = in_data['city']
            if (city == ''):
                city = "<MISSING>"
            state = in_data['state_abbr']
            if (state == ''):
                state = "<MISSING>"
            address_full = in_data['address_full']
            if (address_full == ''):
                address_full = "<MISSING>"
            store_zip = address_full.split(",")[1].split(" ")[-1]
            if (store_zip == ''):
                store_zip = "<MISSING>"
            store_id = in_data['id']
            if (store_id == ''):
                store_id = "<MISSING>"
            phone = in_data['phone']
            if (phone == ''):
                phone = "<MISSING>"
            lat = in_data['latitude']
            if (lat == ''):
                lat = "<MISSING>"
            lag = in_data['longitude']
            if (lag == ''):
                lag = "<MISSING>"

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
            return_object.append("Cobblestone Hotels")
            return_object.append(lat)
            return_object.append(lag)
            return_object.append("<MISSING>")
            return_main_object.append(return_object)

    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
