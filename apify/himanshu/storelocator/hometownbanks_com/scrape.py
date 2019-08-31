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

    base_url = "https://www.hometownbanks.com"
    r = requests.get("https://www.hometownbanks.com/Locations", headers=headers)
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
    location_type = "hometownbanks"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    # print("data ====== "+str(soup))
    for script in soup.find_all("img", {"id": re.compile("MainContent_rptLocations_imgLocation")}):
        parent_script = script.parent

        tag_location = parent_script.find_all('div', {"class": re.compile("oneFourthWidth")})
        if tag_location is not None:
            list_location = list(tag_location[0].stripped_strings)

            if 'Has ATM' in list_location:
                list_location.remove('Has ATM')

            list_hours = []
            if len(tag_location) > 1:
                list_hours = list(tag_location[1].stripped_strings)

            street_address = list_location[0]

            city = list_location[0].split(",")[0]

            if "-" in list_location[-1]:
                phone = list_location[-1]
            else:
                phone = "<MISSING>"

            zipp = list_location[1].split(",")[1].strip().split(" ")[-1]
            state = list_location[1].split(",")[1].strip().split(" ")[-2]
            location_name = city
            country_code = "US"

            location_type = "hometownbanks"
            if len(list_hours) > 0:
                hours_of_operation = " ".join(list_hours)
            else:
                hours_of_operation = "<MISSING>"
                location_type = location_type + " has ATM"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            # print("list_location = " + str(list_location))
            # print("phone = " + str(phone))
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
