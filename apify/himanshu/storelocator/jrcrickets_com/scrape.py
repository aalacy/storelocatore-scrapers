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

    base_url = "https://www.jrcrickets.com"
    r = requests.get("http://jrcrickets.com/locations.php", headers=headers)
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
    location_type = "jrcrickets"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    # print("data ====== "+str(soup))
    for script in soup.find_all("div", {"class": "each_loc"}):
        list_location = list(script.stripped_strings)

        if 'More info' in list_location:
            list_location.remove('More info')

        # print(str(len(list_location)) + " ==== script === " + str(list_location))

        location_name = list_location[0]
        street_address = list_location[1]
        country_code = "US"
        city_state_zipp = list_location[2].replace('US', "").split(",")

        if len(city_state_zipp) > 1:
            city = city_state_zipp[0]
            state = city_state_zipp[1].strip().split(" ")[0]
            zipp = city_state_zipp[1].strip().split(" ")[1]
        else:
            city_state_zipp = city_state_zipp[0].strip()
            # city_state_zipp = city_state_zipp[0].replace("  "," ")
            if len(city_state_zipp.split(' ')[-1]) == 5:
                state = city_state_zipp.replace('  ', " ").split(' ')[-2]
                zipp = city_state_zipp.replace('  ', " ").strip().split(' ')[-1]
                city = " ".join(city_state_zipp.replace('  ', " ").strip().split(' ')[:-2])
            else:
                state = "<MISSING>"
                zipp = "<MISSING>"
                city = "<MISSING>"
                if city_state_zipp.split(" ")[0].isdigit():
                    street_address = city_state_zipp

        for str_data in list_location:
            if "Hours:" in str_data:
                hours_of_operation = str_data.replace("Hours:", "")

        if len(hours_of_operation) == 0:
            hours_of_operation = "<MISSING>"

        for str_data in list_location:
            if "Phone:" in str_data:
                phone = str_data.replace("Phone:", "")

        if len(phone) == 0:
            try:
                phone_index = list_location.index("Phone:")
                if len(list_location[phone_index + 1]) == 12:
                    phone = list_location[phone_index + 1]
                else:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"

        # print("street_address === " + str(street_address))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
