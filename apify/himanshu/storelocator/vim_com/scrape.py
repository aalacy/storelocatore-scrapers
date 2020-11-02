import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('vim_com')





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

    base_url = "https://www.vim.com"
    r = session.get("https://www.vim.com/apps/store-locator", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "vim"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    list_locations = soup.text.split("markersCoords.push({")

    for script in list_locations[1:-2]:
        soup_location = script.split("});")[0]

        list_location = soup_location.split(",")
        # logger.info(str(len(list_location)) + " == list_locations ====== " + str(list_location))

        latitude = list_location[0].replace("lat:", "").strip()
        longitude = list_location[1].replace("lng:", "").strip()
        store_number = list_location[2].replace("id:", "").strip()

        address_str = list_location[5].replace("address:'", "").strip().replace("&#039;", "\"").replace("&lt;",
                                                                                                        "<").replace(
            "&gt;", ">")
        address_soup = BeautifulSoup(address_str, "lxml")
        address_list = list(address_soup.stripped_strings)
        location_name = address_list[0]
        street_address = address_list[1]
        city = address_list[2]

        sz_str = list_location[6].replace("address:'", "").strip().replace("&#039;", "\"").replace("&lt;", "<").replace(
            "&gt;", ">")
        sz_str_soup = BeautifulSoup(sz_str, "lxml")
        sz_str_list = list(sz_str_soup.stripped_strings)
        # logger.info("address == " + str(sz_str_list))
        if len(sz_str_list) > 1:
            state = sz_str_list[0]
            zipp = sz_str_list[1]
        else:
            zipp = sz_str_list[0]
            state = "<MISSING>"

        country_code = "US"

        r_phone_hour = session.get("https://stores.boldapps.net/front-end/get_store_info.php?shop=vimstores.myshopify.com&data=detailed&store_id="+store_number, headers=headers)
        soup_phone_hour = BeautifulSoup(r_phone_hour.text, "lxml")

        phone = soup_phone_hour.find('span',{"class":"phone"}).text.split("Fax:")[0]
        hours_of_operation = soup_phone_hour.find('span',{"class":"phone"}).text.split("M-F:")[1].replace("\"}","")
        # logger.info("soup_location ===== "+str(soup_phone_hour))
        # logger.info("phone ===== "+phone)
        # logger.info("hours_of_operation ===== "+hours_of_operation)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
 




