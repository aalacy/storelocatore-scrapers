import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ulta_com')


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
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.ulta.com"
    r = session.get('https://api.sweetiq.com/store-locator/public/locations/582b2f2f588e96c131eefa9f?categories=&geo%5B0%5D=-95.7129&geo%5B1%5D=37.0902&tag=&perPage=1000000000000&page=1&search=&searchFields%5B0%5D=name&clientIds%5B0%5D=57b75cf805fbd94379859661&box%5B0%5D=-180&box%5B1%5D=-71.03870026971174&box%5B2%5D=180&box%5B3%5D=71.03870026970304', headers=headers)
    data = r.json()['records']
    soup = BeautifulSoup(r.text, "lxml")
    for store_data in data:
        store = []
        # logger.info(store_data)
        # exit()
        location_name = store_data['mallName']
        street_address = store_data['address']
        city = store_data['city']
        state = store_data['province']
        store_zip = store_data['postalCode'].strip()
        if len(store_zip) == 4:
            store_zip = "0" + store_zip
        phone = store_data['phone']
        store_number = store_data["branch"]
        page_url = store_data["website"]
        if(location_name == '' or location_name is None):
            location_name = "<MISSING>"
        if (street_address == '' or state is None):
            street_address = "<MISSING>"
        if (city == '' or state is None):
            city = "<MISSING>"
        if (state == '' or state is None):
            state = "<MISSING>"
        if (store_zip == '' or store_zip is None):
            store_zip = "<MISSING>"
        if (phone == '' or phone is None):
            phone = "<MISSING>"
        if (store_number == '' or store_number is None):
            store_number = "<MISSING>"
        if "Sun" in store_data['hoursOfOperation']:
            for Sun in store_data['hoursOfOperation']['Sun']:
                sun_time = 'Sun: ' + Sun[0] + ' - ' + Sun[1]
        else:
            sun_time=""
        for Sat in store_data['hoursOfOperation']['Sat']:
            sat_time = 'Sat: ' + Sat[0] + ' - ' + Sat[1]
        for Fri in store_data['hoursOfOperation']['Fri']:
            fri_time = 'Fri: ' + Fri[0] + ' - ' + Fri[1]
        for Thu in store_data['hoursOfOperation']['Thu']:
            thu_time = 'Thu: ' + Thu[0] + ' - ' + Thu[1]
        for Wed in store_data['hoursOfOperation']['Wed']:
            wed_time = 'Wed: ' + Wed[0] + ' - ' + Wed[1]
        for Tue in store_data['hoursOfOperation']['Tue']:
            tue_time = 'Tue: ' + Tue[0] + ' - ' + Tue[1]
        for Mon in store_data['hoursOfOperation']['Mon']:
            mon_time = 'Mon: ' + Sat[0] + ' - ' + Mon[1]
        hour = mon_time + ', ' + tue_time + ', ' + wed_time + ', ' + \
            thu_time + ', ' + fri_time + ', ' + sat_time + ', ' + sun_time
        if (hour == '' or hour is None):
            hour = "<MISSING>"
        return_object = []
        return_object.append(base_url)
        return_object.append(location_name)
        return_object.append(street_address)
        return_object.append(city)
        return_object.append(state)
        return_object.append(store_zip)
        return_object.append("US")
        return_object.append(store_number)
        return_object.append(phone)
        return_object.append("<MISSING>")
        return_object.append(store_data["geo"][1])
        return_object.append(store_data["geo"][0])
        return_object.append(hour)
        return_object.append(page_url)
        yield return_object
        # logger.info("--" + str(str(return_object)))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~")


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
