import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "https://www.rosesdiscountstores.com"
    # zips = sgzip.for_radius(100)
    addresses = []

    r = requests.get(
        "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=82.292272%2C90.108768&southwest=-57.393433%2C-180").json()

    for vj in r['locations']:

        locator_domain = base_url

        location_name = vj['name']
        street_address = vj['address1'].strip()

        vk = vj['address'].split(',')[2].strip().split(' ')[0].strip()
        # print(vk)
        us_zip_list = re.findall(re.compile(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(vj['address']))
        if us_zip_list:
            zipp = us_zip_list[-1]
        # print(zipp)
        # print(us_zip_list)

        city = vj['city'].strip()

        state = vj['region'].strip()
        # zip = vj['postcode'].strip()

        hours_of_operation = ''
        if "hoursOfOperation" in vj['hours']:
            for i in vj['hours']['hoursOfOperation']:
                hours_of_operation = hours_of_operation + ' ' + \
                    i + ' ' + vj['hours']['hoursOfOperation'][i]

        if "con_wg5rd22k" in vj['contacts']:
            phone = vj['contacts']['con_wg5rd22k']['text']
        else:
            phone = "<MISSING>"
        store_number = "<MISSING>"

        country_code = vj['countryCode'].strip()
        location_type = '<MISSING>'
        latitude = vj['lat']
        longitude = vj['lng']
        page_url = "<MISSING>"
        if street_address in addresses:
            continue
        addresses.append(street_address)

        # hours_of_operation = ''
        # if 'hoursOfOperation' in   vj['hours']:
        #     hours_of_operation = ' mon ' + vj['hours']['hoursOfOperation']['mon'] + ' tue ' + vj['hours']['hoursOfOperation']['tue'] + ' thu ' + vj['hours']['hoursOfOperation']['thu'] + ' fri ' + vj['hours']['hoursOfOperation']['fri'] + ' sat ' + vj['hours']['hoursOfOperation']['sat'] + ' sun ' + vj['hours']['hoursOfOperation']['sun']

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        # print('===', str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
