import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sys
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('yojie_com')





session = SgRequests()

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.yojie.com"
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "https://www.yojie.com/locations.html"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # logger.info(soup.prettify())
    coord = []
    l1 = soup.find(lambda tag: (tag.name == "script")
                   and "initMap" in tag.text).text.split("var artesia =")[1].split(';')[0]
    l2 = soup.find(lambda tag: (tag.name == "script")
                   and "initMap" in tag.text).text.split("var lasvegas =")[1].split(';')[0]
    coord.append(l1)
    coord.append(l2)
    c1 = []
    c2 = []
    for coords in coord:
        c1.append(coords.split(',')[0].replace("{lat:", "").strip())
        c2.append(coords.split(',')[1].replace(
            "lng:", "").replace("}", "").strip())

    for loc in soup.find("div", class_="about-us-1").find_all("div", {"class": "locations"}):
        list_loc = list(loc.stripped_strings)
        street_address = list_loc[0].strip()
        city = list_loc[1].split(',')[0].strip()
        state = list_loc[1].split(',')[1].split()[0].strip()
        zipp = list_loc[1].split(',')[1].split()[-1].strip()
        phone = list_loc[2].strip()
        location_name = city
        hours_of_operation = " ".join(list_loc[4:]).strip()
        if c1 != []:
            latitude = c1.pop(0)
        if c2 != []:
            longitude = c2.pop(0)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" else x for x in store]
        # logger.info("data ===" + str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
