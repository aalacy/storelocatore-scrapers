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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://eggsquis.com"
    r = session.get(base_url +'/succursales/' , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    json_data = soup.text.split("var g = ")[1]
    json_data = json_data.split("var actions")[0]
    json_data = json_data.replace(';', ' ')
    data = json.loads(str(json_data))

    res_data =data['restaurants']
    for r_data in res_data:
        location_name = r_data['name'].strip()
        if(location_name == ''):
            location_name = "<MISSING>"
        store_id = r_data['id']
        if (store_id == ''):
            store_id = "<MISSING>"
        street_address = r_data['contact']['adress'].strip()
        if (street_address == ''):
            street_address = "<MISSING>"
        city = r_data['contact']['city'].strip()
        if (city == ''):
            city = location_name.replace("Montréal","").strip()
        phone = r_data['contact']['phone']
        if (phone == ''):
            phone = "<MISSING>"
        state = r_data['contact']['province'].strip()
        if (state == ''):
            state = "<MISSING>"
        store_zip = r_data['contact']['zip']
        if (store_zip == ''):
            store_zip = "<MISSING>"
        lat = r_data['coords']['lat']
        if (lat == ''):
            lat = "<MISSING>"
        lag = r_data['coords']['lng']
        if (lag == ''):
            lag = "<MISSING>"
        hour = 'THE : '+r_data['hours']['1']['from']+'h to '+r_data['hours']['1']['to'] + 'h, V : '+r_data['hours']['2']['from']+'h to '+r_data['hours']['2']['to'] + 'h, M : '+r_data['hours']['3']['from']+'h to '+r_data['hours']['3']['to'] + 'h, S : '+r_data['hours']['4']['from']+'h to '+r_data['hours']['4']['to'] + 'h, M : '+r_data['hours']['5']['from']+'h to '+r_data['hours']['5']['to'] + 'h, D : '+r_data['hours']['6']['from']+'h to '+r_data['hours']['6']['to'] + 'h, J : '+r_data['hours']['7']['from']+'h to '+r_data['hours']['7']['to']+'h'
        if (hour == ''):
            hour = "<MISSING>"
        return_object = []
        return_object.append(base_url)
        return_object.append("<MISSING>")
        return_object.append(location_name)
        return_object.append(street_address)
        return_object.append(city)
        return_object.append(state)
        return_object.append(store_zip)
        return_object.append("CA")
        return_object.append(store_id)
        return_object.append(phone)
        return_object.append("<MISSING>")
        return_object.append(lat)
        return_object.append(lag)
        return_object.append(hour)
        return_main_object.append(return_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
