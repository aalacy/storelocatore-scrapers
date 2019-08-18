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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "http://www.lionschoice.com"
    r = requests.get("http://www.lionschoice.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "lionschoice"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find('ul', {'class': 'medium-block-grid-3'}).find_all('li'):
        list_store_data = list(script.stripped_strings)

        if 'More Details' in list_store_data:
            list_store_data.remove('More Details')

        if 'Delivery' in list_store_data:
            list_store_data.remove('Delivery')

        if 'Order Online' in list_store_data:
            list_store_data.remove('Order Online')

        if 'Download Breakfast Menu' in list_store_data:
            list_store_data.remove('Download Breakfast Menu')

        if len(list_store_data) > 1:
            print(str(len(list_store_data)) + ' = list_store_data === ' + str(list_store_data))

            location_name = list_store_data[0]
            street_address = list_store_data[1]
            city = ' '.join(list_store_data[2].strip().split(' ')[:-2])
            state = list_store_data[2].strip().split(' ')[-2]
            # state = list_store_data[2].strip()[:-5].strip().replace('.',"")
            zipp = list_store_data[2].strip().split(' ')[-1]
            phone = list_store_data[3]
            country_code = 'US'

            if 'Business Hours:' in list_store_data:
                hours_of_operation = ", ".join(list_store_data[list_store_data.index('Business Hours:'):])
            elif 'Dining Room:' in list_store_data:
                hours_of_operation = ", ".join(list_store_data[list_store_data.index('Dining Room:'):])
            elif 'Dining Room Hours:' in list_store_data:
                hours_of_operation = ", ".join(list_store_data[list_store_data.index('Dining Room Hours:'):])
            else:
                hours_of_operation = ", ".join(list_store_data[list_store_data.index('Open Daily'):])

            latitude = '<MISSING>'
            longitude = '<MISSING>'

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            print("data = " + str(store))
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
