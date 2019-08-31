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

    base_url = "https://www.educationaloutfitters.com"
    r = requests.get("http://www.educationaloutfitters.com/states", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
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
    location_type = "educationaloutfitters"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for script_location in soup.find_all("div", {"class": "p-name"}):
        location_url = script_location.find('a')['href']
        r_location = requests.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")
        # print("location_url === "+location_url)

        for script_reservation_a in soup_location.find_all("div", {"class": "ProductDetailsGrid ProductAddToCart"}):
            address_list = list(script_reservation_a.stripped_strings)
            address_list = [x for x in address_list if "Outfitter" not in x]

            for i in range(len(address_list)):
                address_list[i] = re.sub('[^A-Za-z0-9 ]+', '', address_list[i])

            while "" in address_list:
                address_list.remove("")

            for phone in address_list:
                if len(phone) == 10 and phone.isdigit():
                    break

            # print("address_list === "+str(address_list))

            if any(char.isdigit() for char in address_list[0]):
                street_address = address_list[0]
                if address_list[1][-5:].isdigit():
                    zipp = address_list[1][-5:]
                    state = address_list[1][-8:-6]
                    city = address_list[1][:-8]
                else:
                    zipp = address_list[2][-5:]
                    state = address_list[2][-8:-6]
                    city = address_list[1]

            else:
                street_address = "<MISSING>"
                zipp = "<MISSING>"
                state = "<MISSING>"
                city = "<MISSING>"
                if len(address_list[0].split(" ")[-1]) == 2:
                    state = address_list[0].split(" ")[-1]
                    city = address_list[0].split(" ")[0]

            hours_of_operation = "<MISSING>"
            location_name = city


            # print("street_address === "+str(street_address))
            # print("zipp === "+str(zipp))
            # print("state === "+str(state))
            # print("city === "+str(city))


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
