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

    print("soup ===  first")

    base_url = "https://www.eileenscookies.com"
    r = session.get("https://www.eileenscookies.com/locations/", headers=headers)
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
    phone = "<MISSING>"
    location_type = "bergmanluggage"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all("div", {"class": "store-thumbnail cell"}):
        store_url = script.find('a')['href']
        r_store = session.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")

        try:
            phone = soup_store.find('div', {'id': 'store-left'}).find('a', {'href': re.compile('tel:')}).text
        except:
            phone = "<MISSING>"

        address = ",".join(list(soup_store.find('div', {'id': 'store-address'}).stripped_strings))

        street_address = address.split(",")[1]
        city = address.split(",")[2]
        location_name = address.split(",")[-2]
        state = address.split(",")[-1].split(" ")[-2]
        zipp = address.split(",")[-1].split(" ")[-1]
        country_code = "US"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = ",".join(list(soup_store.find('div', {'id': 'store-hours'}).stripped_strings))

        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "+address)
        #
        # print("locator_domain = " + locator_domain)
        # print("location_name = " + location_name)
        # print("street_address = " + street_address)
        # print("city = " + city)
        # print("state = " + state)
        # print("zipp = " + zipp)
        # print("location_name = " + location_name)
        # print("country_code = " + country_code)
        # print("store_number = " + store_number)
        # print("phone = " + phone)
        # print("location_type = " + location_type)
        # print("latitude = " + latitude)
        # print("longitude = " + longitude)
        # print("hours_of_operation = " + hours_of_operation)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
