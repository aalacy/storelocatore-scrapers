import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.thinkrogers.com"
    r = session.get(
        "https://www.thinkrogers.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())

    return_main_object = []

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
    location_type = "thinkrogers"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    val = soup.find('div', class_="row-fluid footer-inner").find('div', class_="sub-footer").find('div',
                                                                                                  class_='wrap-inner')
    for details in val.find('div', class_="footer-columns").find_all('div', {'itemprop': 'address'}):
        list_details = list(details.stripped_strings)

        del list_details[0]

        while ',' in list_details:
            list_details.remove(',')
        size = len(list_details)
        idx_list = [idx + 1 for idx,
                    val in enumerate(list_details) if "Address" in val]
        res = [list_details[i: j] for i, j in
               zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))]

        del res[0][0]
        for x in res:
            del x[-1]
            del x[4]
            del x[-2]
        # print(str(res))
        for single_list in res:
            # print(single_list)
            street_address = "".join(single_list[0])
            city = "".join(single_list[1])
            state = "".join(single_list[2])
            zipp = "".join(single_list[3])
            phone = "".join(single_list[-1])
            hours_of_operation = " ".join(single_list[4:-1])
            location_name = "Rogers Jewelry Co, " + city

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]
            store = ["<MISSING>" if x == "" else x for x in store]
            return_main_object.append(store)
            print("data = " + str(store))
            print(
                '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
