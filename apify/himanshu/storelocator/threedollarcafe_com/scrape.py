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



    base_url = "https://www.threedollarcafe.com"
    r = requests.get("https://www.threedollarcafe.com/our-locations/", headers=headers)

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
    location_type = "threedollarcafe"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    for script in soup.find_all('div', {'class': 'location-detail'}):
        list_address = list(script.find('p', {'class', 'address'}).stripped_strings)
        # print("list_address = " + str(list_address))

        location_name = list_address[0]
        street_address = list_address[1].split(',')[0]
        city = list_address[1].split(',')[-2]
        state = list_address[1].split(',')[-1].strip().split(' ')[-2]
        zipp = list_address[1].split(',')[-1].strip().split(' ')[-1].split('-')[0]
        country_code = 'US'

        phone = script.find('i', {'class', 'fa fa-phone-square'}).parent.text.strip()

        hours_of_operation = ' '.join(list(script.find('p',{'class':'day-time'}).stripped_strings))

        # hours_of_operation = hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip()

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
