import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('yesway_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    base_url = "https://yesway.com"
    r = session.get("https://yesway.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    addresses = []
    for location in soup.find_all("div", {'class': "panel"}):

        try:
            address = list(location.find("address").stripped_strings)
            street_address = address[0]
            city = address[-1].split(",")[0]
            state = address[-1].split(",")[-1].split(" ")[1]
            zipp = address[-1].split(",")[-1].split(" ")[-1]
            name = location.find("div", {'class': "thumbnail"}).find(
                "h4").text.split("(")[0]
            hours = " ".join(
                list(location.find("ul", {'class': "list-unstyled"}).stripped_strings))
            marker = json.loads(location.find("marker")["position"])
            # if "63471" == zipp:
            #     logger.info(address)

        except:
            pass

        if address in addresses:
            continue
        addresses.append(address)
        store = []
        store.append("https://yesway.com")
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(name.split("#")[1].replace(" ", ""))
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(marker[0])
        store.append(marker[1])
        store.append(hours)
        store.append("https://yesway.com/locations/")
        return_main_object.append(store)
        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
