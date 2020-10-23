import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('eileenscookies_com')





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

    logger.info("soup ===  first")

    base_url = "https://www.eileenscookies.com"
    r = session.get("https://www.eileenscookies.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

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

        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "+address)
        #
        # logger.info("locator_domain = " + locator_domain)
        # logger.info("location_name = " + location_name)
        # logger.info("street_address = " + street_address)
        # logger.info("city = " + city)
        # logger.info("state = " + state)
        # logger.info("zipp = " + zipp)
        # logger.info("location_name = " + location_name)
        # logger.info("country_code = " + country_code)
        # logger.info("store_number = " + store_number)
        # logger.info("phone = " + phone)
        # logger.info("location_type = " + location_type)
        # logger.info("latitude = " + latitude)
        # logger.info("longitude = " + longitude)
        # logger.info("hours_of_operation = " + hours_of_operation)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
