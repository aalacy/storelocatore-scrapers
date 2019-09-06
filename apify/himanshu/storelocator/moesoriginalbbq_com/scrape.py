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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # print("soup ===  first")

    base_url = "https://www.moesoriginalbbq.com/"
    r = requests.get("https://api.storepoint.co/v1/159d567264b9aa/locations", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "moesoriginalbbq"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    json_data = r.json()

    # print('json_data ===== ' + str(len(json_data['results']['locations'])))

    for location_list in json_data['results']['locations']:

        location_name = location_list['name']
        store_number = location_list['id']
        latitude = location_list['loc_lat']
        longitude = location_list['loc_long']
        phone = "<MISSING>"

        full_address = location_list['streetaddress'].replace("  ", " ")
        if not full_address.find('https://') >= 0:
            if len(full_address.split(',')[-1].strip().split(' ')) > 1:
                street_address = ','.join(full_address.split(',')[:-2])
                city = full_address.split(',')[-2]
                if len(street_address) == 0:
                    street_address = full_address.split(',')[0]
                    city = '<MISSING>'

                state = full_address.split(',')[-1].strip().split(' ')[0]
                zipp = full_address.split(',')[-1].strip().split(' ')[1][-5:]
            else:
                street_address = ','.join(full_address.split(',')[:-3])
                city = full_address.split(',')[-3]
                if str(full_address.split(',')[-1])[-5:].isdigit():
                    zipp = full_address.split(',')[-1][-5:]
                    state = full_address.split(',')[-2]
                else:
                    zipp = full_address.split(',')[-2][-5:]
                    state = full_address.split(',')[-1]
        else:
            street_address = "<MISSING>"
            city = "<MISSING>"
            zipp = "<MISSING>"
            state = "<MISSING>"

        # print("data === " + str(full_address))
        location_url = location_list['website']
        r_location = requests.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        if soup_location.find('div', {'class': re.compile('page-')}) is not None:
            list_address = list(soup_location.find('div', {'class': re.compile('page-')}).stripped_strings)
            hours_of_operation = ', '.join(list(soup_location.find('h2').stripped_strings))
            # print("location_url `````````````  " + str(location_url))
            # print("list_hours ~~~~~~~~~~  " + str(hours_of_operation))

            phone_index = [i for i, s in enumerate(list_address) if 'Phone' in s]

            if len(list_address) > 0 and len(phone_index) > 0:
                if len((list_address[phone_index[0]]).split(':')) > 1:
                    phone = str(list_address[phone_index[0]]).split(':')[-1].strip()
                else:
                    phone = str(list_address[phone_index[0]+1])
            # print("phone =====  " + phone)

        if len(phone) == 0:
            phone = '<MISSING>'

        if '<MISSING>' in phone:
            hours_of_operation = '<MISSING>'
        
        phone = str(phone[:14])
        phone = phone.replace('(',"").replace(')',"").replace('-',' ').split(' ')
        phone = ' '.join(["" if not x.isdigit() else x for x in phone])
        

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]
        store = ["<MISSING>" if x == "" else x for x in store]
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
