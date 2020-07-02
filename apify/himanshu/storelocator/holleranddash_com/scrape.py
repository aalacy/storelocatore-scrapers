import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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

    #print("soup ===  first")

    base_url = "https://holleranddash.com"
    r = session.get("https://holleranddash.com/locations/", headers=headers)
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
    location_type = "holleranddash"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    # print("data ====== "+str(soup))
    for script in soup.find("ul", {"id": "locations-list"}).find_all("li", {"id": re.compile("location-")}):
        list_location = list(script.stripped_strings)

        # print("list_location === " + str(list_location))

        location_name = list_location[0]
        street_address = list_location[1]
        city = list_location[2].split(",")[0]
        state = list_location[2].split(",")[1].strip().split(" ")[-2]
        zipp = list_location[2].split(",")[1].strip().split(" ")[-1]
        country_code = "US"
        phone = list_location[3]

        detail_url = base_url + script.find("p", {"class": "store-details"}).find('a')['href']
        # print("detail_url == " + detail_url)
        r_hours = session.get(detail_url, headers=headers)
        soup_hours = BeautifulSoup(r_hours.text, "lxml")

        for script_hour in soup_hours.find_all("div", {"class": "wpb_wrapper"}):
            if script_hour.find("p", {"class": "address"}) is not None:
                list_hour = list(script_hour.stripped_strings)
                list_hour = list_hour[:list_hour.index("Events")]
                # print(str(len(list_hour)) + " === list_hour === " + str(list_hour))

                hours_of_operation = " ".join(list_hour[list_hour.index("open today"):])

                map_location = script_hour.find('a')['href'];
                latitude = map_location.split("/@")[1].split(",")[0]
                longitude = map_location.split("/@")[1].split(",")[1]
                # print("map_location === "+map_location)
                # print("latitude === "+latitude)
                # print("longitude === "+longitude)

                break

        # print("hours_of_operation === "+hours_of_operation)

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
