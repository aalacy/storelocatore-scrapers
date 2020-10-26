import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('xscapetheatres_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://xscapetheatres.com/"
    r = session.get(base_url + '/location', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("li", {"class": "subNavContainer"}):
        if(parts.find("a", {"id": "nav_locations"})):
            semi_ul = parts.find("ul", {"class": "subNav"})
            for semi_parts in semi_ul.find_all("li"):
                return_object = []
                store_request = session.get(base_url + semi_parts.find("a")['href'])
                re_url = base_url + semi_parts.find("a")['href'];
                store_number = re_url.split("/")[-2]
                store_soup = BeautifulSoup(store_request.text, "lxml")
                temp_storeaddresss = store_soup.find("div", {"id": "t_info"})
                if (temp_storeaddresss.find("p")):
                    temp_store = list(temp_storeaddresss.find_all("p")[0].stripped_strings)
                    location_name = temp_store[0]
                    street_address = temp_store[1]
                    city = temp_store[2].split(",")[0]
                    state_zip = temp_store[2].split(",")[1]
                    state = state_zip.split(" ")[1]
                    store_zip = state_zip.split(" ")[2]
                    temp_number = list(temp_storeaddresss.find_all("p")[1].stripped_strings)
                    phone = temp_number[1]
                    return_object.append(base_url)
                    return_object.append(location_name)
                    return_object.append(street_address)
                    return_object.append(city)
                    return_object.append(state)
                    return_object.append(store_zip)
                    return_object.append("US")
                    return_object.append(store_number)
                    return_object.append(phone)
                    return_object.append("xscape theatres")
                    return_object.append("<MISSING>")
                    return_object.append("<MISSING>")
                    return_object.append("<MISSING>")
                    logger.info(return_object)
                    return_main_object.append(return_object)
    logger.info(return_main_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()