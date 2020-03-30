import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup, Comment
import re
import json




session = SgRequests()

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # it will used in store data.
    locator_domain = "https://ibabc.org/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get("https://ibabc.org/index.php?option=com_storelocator&view=map&format=raw&searchall=0&Itemid=511&lat=49.2843731&lng=-123.11644030000002&radius=1000000&catid=-1&tagid=-1&featstate=0&name_search=", headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    for x in soup.find_all("marker"):
        location_name = x.find("name").text
        latitude = x.find('lat').text
        longitude = x.find("lng").text

        if "-" == x.find('phone').text:
            phone = "<MISSING>"
        else:
            phone = x.find('phone').text
        address = x.find('address')
        address_list = list(address)

        street_address = "".join(address_list).split(',')[0]
        state_tag = "".join(address_list).split(',')[-1]
        state_list = state_tag.split()
        if len(state_list) == 1:
            state = state_list[0]
            # print(state)
            if "Burnaby" == state:
                state = "<MISSING>"
        elif len(state_list) == 2:
            if hasNumbers(state_list[-1]):
                state = address_list[0].split(',')[-2].split()[-1].strip()
                if "Vancouver" == state:
                    state = "<MISSING>"
            else:
                state = state_list[-1].strip()
        elif len(state_list) == 3:
            state = state_list[0].strip()
        elif len(state_list) == 4:
            state = state_list[1]
        elif len(state_list) == 5:
            state = state_list[2].strip()
            if "St." == state:
                state = state_list[-1].strip()
        else:
            pass

        # print(state_tag)
        # if hasNumbers(state_tag):
        #     state_list = re.findall(r' ([A-Z]{2}) ', str(state_tag))
        #     if state_list != []:
        #         state = state_list[0].strip().replace(
        #             'Vancouver', '').replace('Richmond', '').strip()
        #     else:
        #         # print(address_list)
        #         state = "<MISSING>"
        # else:

        #     state = state_tag.strip().replace('Vancouver', '').replace('Richmond', '').strip()
        if "Burnaby" in state:
            state = "<MISSING>"
        c_list = "".join(address_list).split(',')[1].split()
        if len(c_list) == 1:
            city = "".join(c_list)
        if len(c_list) == 2 and ("BC" != c_list[-1] and "0B5" != c_list[-1]):
            city = " ".join(c_list)
            # print(city)
        if len(c_list) == 2 and ("BC" == c_list[-1]):
            city = "".join(c_list[0])
            # print(city)
        if "0B5" == c_list[-1]:
            city = "North Vancouver"

        ca_zip_list = re.findall(
            r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str("".join(address_list)))
        if ca_zip_list:
            zipp = ca_zip_list[0].strip()
        else:
            zipp = "<MISSING>"
        # if "3437 Main Street" == street_address:
        #     state  = ad

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" else x for x in store]
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
