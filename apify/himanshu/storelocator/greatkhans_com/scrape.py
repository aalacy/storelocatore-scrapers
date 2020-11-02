import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('greatkhans_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    # logger.info("soup ===  first")

    base_url = "https://www.greatkhans.com"
    r = session.get("http://www.greatkhans.com/menu", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<INACCESSIBLE>"
    city = "<INACCESSIBLE>"
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "http://www.greatkhans.com/menu"

    # logger.info("data ====== "+str(soup))
    for script in soup.find_all("div", {"class": "menu-item"})[1:]:
        list_location = list(script.stripped_strings)

        location_name = list_location[0]
        raw_address = list_location[1].replace(',', "")[:-9]
        country_code = "US"
        # logger.info(list_location)
        address = list_location[1].split()
        street_address = " ".join(
            address[:-3]).replace("Santa", "").replace("San", "").replace("Thousand", "").replace("Sherman", "").replace("ta", "").strip()
        # logger.info(street_address)
        city = " ".join(address[-4:-2]).replace("FC1",
                                                "").replace("Center.", "").replace(",", "").strip()
        if "3rd Floor" == city:
            city = " ".join(address[3:5]).strip()
            street_address = " ".join(
                address[:4]).strip() + " ".join(address[6:])
        us_zip_list = re.findall(re.compile(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(list_location)))

        state_list = re.findall(r' ([A-Z]{2}) ', str(" ".join(list_location)))
        if us_zip_list:
            zipp = us_zip_list[-1].strip()
        else:
            zipp = "<MISSING>"
        if state_list:
            state = state_list[0].strip()
        else:
            state = list_location[1].split(",")[0].split()[-1].strip()
            #logger.info(state)

        # logger.info("list_location ===== "+str(list_location))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
