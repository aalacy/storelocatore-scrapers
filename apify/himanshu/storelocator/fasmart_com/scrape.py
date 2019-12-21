import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import geonamescache

# gc = geonamescache.GeonamesCache()
# countries = gc.get_cities()
# print countries dictionary
# print(countries)


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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    addresses = []
    base_url = "https://fasmart.com"
    r = requests.get(
        "https://gpminvestments.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = "action=wpgmza_sl_basictable&security=fc0b57223a&map_id=7"
    for state in soup.find_all("a", {"name": re.compile("marker")}):
        data = data + "&marker_array%5B%5D=" + \
            state["name"].replace("marker", "")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    r = requests.post(
        "https://gpminvestments.com/wp-admin/admin-ajax.php", headers=headers, data=data)
    soup = BeautifulSoup(r.text, "lxml")
    for location in soup.find("div").find_all("div", recursive=False):
        geo_location = location.find("a", text="Directions")["gps"]
        latitude = geo_location.split(",")[0].strip()
        longitude = geo_location.split(",")[1].strip()
        if "" == latitude:
            latitude = "<MISSING>"
        if "" == longitude:
            longitude = "<MISSING>"
        location_details = list(location.stripped_strings)
        state_split = re.findall("([A-Z]{2})", location_details[1])
        if state_split:
            state = state_split[-1].strip()
            if state == "US":
                state = state_split[-2].strip()
            # if state == "SE":
            #     print(state_split)
        else:
            state = "<MISSING>"

        store_zip_split = re.findall(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b", location_details[1])
        if store_zip_split:
            store_zip = store_zip_split[-1]
            if location_details[1].split(" ")[0] == store_zip:
                store_zip = "<MISSING>"
        else:
            store_zip = "<MISSING>"
        location_details[1] = location_details[1].replace(
            location_details[0], "").replace("\t", " ")

        address_list = location_details[1].split(',')
        if " USA" in address_list:
            address_list.remove(" USA")
        if " United States" in address_list:
            address_list.remove(" United States")
        if len(address_list) == 1:
            address = location.find("a", text="Directions")[
                "wpgm_addr_field"].split('\t')
            if len(address) > 3:
                city = address[-3].strip()
                street_address = " ".join(address[:-3]).strip()
            elif len(address) == 2:
                city = address[-2].strip()
                street_address = address[0].strip()
            else:
                if len(address[0].split("  ")) > 1:
                    if " " != address[0].split("  ")[-1]:
                        if len(address[0].split("  ")) == 3:
                            street_address = address[0].split("  ")[0].strip()
                            city = address[0].split("  ")[1].strip()
                        else:
                            if len(address[0].split("  ")[-1].split()) > 2:
                                city = address[0].split(
                                    "  ")[-1].split()[0].strip()
                                street_address = address[0].split("  ")[
                                    0].strip()
                            else:
                                city = address[0].split(
                                    "  ")[0].split()[-1].strip()
                                street_address = " ".join(address[0].split("  ")[
                                                          0].split()[:-1]).strip()

                    else:
                        city = address[0].split("  ")[0].split()[-3].strip()
                        street_address = " ".join(address[0].split("  ")[
                                                  0].split()[:-3]).strip()
                else:
                    city = "<INACCESSIBLE>"
                    street_address = "<INACCESSIBLE>"
                    # print(address[0].split("  "))
                    # print(len(address[0].split("  ")))
                    # print("~~~~~~~~~~~~~~~~~~~~~")

        elif len(address_list) == 2:
            street_address = " ".join(" ".join(address_list).split()[
                                      :-2][:-1]).replace("North Pleasant", "")
            city = " ".join(address_list).split()[:-2][-1]
            if "Hill" == city:
                city = " ".join(" ".join(address_list).split()
                                [:-2][-3:]).strip()

        else:
            street_address = address_list[0].strip()
            city = address_list[-2].strip()

        store = []
        store.append("https://fasmart.com")
        store.append(location_details[0])
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append(location["mid"])
        store.append("<MISSING>")  # phone
        store.append("<MISSING>")  # location_type
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")  # hours_of_operation
        store.append("<MISSING>")  # page_url
        if store[1] + " " + store[2] in addresses:
            continue
        addresses.append(store[1] + " " + store[2])
        return_main_object.append(store)
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]
        store = ["<MISSING>" if x == "" or x == "  " else x for x in store]
        # print("data == " + str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
