import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

    addresses = []

    base_url = "https://www.hyperionpublic.com"
    r = requests.get("https://www.hyperionpublic.com/", headers=headers,verify=False)
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
    location_type = "hyperionpublic"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    # print("data ====== "+str(soup))
    for script in soup.find("div", {"id": "SITE_FOOTERcenteredContent"}).find_all("div", {"id": re.compile("comp-i"),
                                                                                          "class": "txtNew",
                                                                                          "data-packed": "true"}):
        list_location = list(script.stripped_strings)

        if len(list_location) > 3:
            street_address = list_location[0]
            city = list_location[1].split(',')[0]
            state = list_location[1].split(',')[1].strip().split(' ')[-2]
            zipp = list_location[1].split(',')[1].strip().split(' ')[-1]
            phone = list_location[2]
            country_code = "US"
            location_name = city

            hours_of_operation = " ".join(list_location[3:]).replace("\xa0", "").replace("\u200b", "").strip()
            # if 'More info' in list_location:
            #     list_location.remove('More info')

            # print(str(len(list_location)) + " ==== script === " + str(list_location))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
