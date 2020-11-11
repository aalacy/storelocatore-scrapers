import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
import urllib.parse
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kellyservices_ca')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    # search.initialize(include_canadian_fsas = True)   # with canada zip
    MAX_RESULTS = 10
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://www.kellyservices.ca"

    loc_search_url = 'https://branchlocator.kellyservices.com/default.aspx?s=&l='
    r_loc_search = session.get(loc_search_url, headers=headers)
    # logger.info("r_loc_search === "+ str(r_loc_search.text))
    soup_loc_search = BeautifulSoup(r_loc_search.text, "lxml")
    view_state = urllib.parse.quote(soup_loc_search.find("input", {"id": "__VIEWSTATE"})["value"])
    event_validation = urllib.parse.quote(soup_loc_search.find("input", {"id": "__EVENTVALIDATION"})["value"])

    while zip_code:
        result_coords = []

        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info("zip_code === " + zip_code)

        # zip_code = 33127
        data = '__VIEWSTATE=' + view_state + '&__EVENTVALIDATION=' + event_validation + '&txtZip=' + str(
            zip_code) + '&btnSearch=+Search'

        # logger.info("data == "+ data)
        # r_locations = session.post("https://branchlocator.kellyservices.com/default.aspx", headers=headers, data=data)

        r_locations = request_wrapper("https://branchlocator.kellyservices.com/default.aspx","post", headers=headers,data=data)

        if r_locations == None:
            search.max_distance_update(MAX_DISTANCE)
            zip_code = search.next_zip()
            continue
        soup_locations = BeautifulSoup(r_locations.text, "lxml")

        current_results_len = len(soup_locations.find_all("a", {
            "onclick": re.compile("setLocation")}))  # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))

        for location in soup_locations.find_all("a", {"onclick": re.compile("setLocation")}):
            # previous_sibling
            geo_url = location["href"].replace("'", "")
            address_list = location["onclick"].replace("setLocation(", "").replace(")", "").replace("'", "").split(",")

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            page_url = ""
            hours_of_operation = ""

            # do your logic here
            # logger.info("geo_url ==== " + str(geo_url))
            # logger.info("r_locations ==== " + str(address_list))

            store_number = location.parent.parent.find_previous_sibling("td").text.strip()

            phone = address_list[-2]
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(address_list))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_list))
            state_list = re.findall(r'([A-Z]{2})', str(address_list))

            if state_list:
                state = state_list[-1]

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            location_name = address_list[0]
            street_address = " ".join(address_list[1:-5]).strip()
            city = address_list[-5]

            latitude = geo_url.split("&sll=")[1].split(",")[0]
            longitude = geo_url.split("&sll=")[1].split(",")[1]

            result_coords.append((latitude, longitude))

            if latitude == '0':
                latitude = ""
            if longitude == '0':
                longitude = ""

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1] + " " + store[2]) not in addresses and country_code:
                addresses.append(str(store[1] + " " + store[2]))

                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if store[2] == store[4]:
                    store[2] = "<MISSING>"
#                logger.info("data = " + str(store))
#                logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
