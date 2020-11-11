import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fredsmeds_com')





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


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 20
    MAX_DISTANCE = 30
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.fredsmeds.com"

    while zip_code:
        try:
            result_coords = []

            # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
            # logger.info("zip_code === " + zip_code)
            # zip_code = "39114"
            location_url = "http://www.fredsmeds.com/locate/?find-a-store=" + zip_code
            r_locations = session.get(location_url, headers=headers)
            soup_locations = BeautifulSoup(r_locations.text, "lxml")

            location_list = soup_locations.find_all("div", {"class": "store-info"})
            current_results_len = len(location_list)  # it always need to set total len of record.

            # logger.info("current_results_len === " + str(current_results_len))

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
            hours_of_operation = ""
            page_url = ""

            for location in location_list:

                page_url = base_url + location.find("a", {"class": "button"})["href"]
                address_list = list(location.stripped_strings)

                location_name = " ".join(address_list[:3])
                store_number = address_list[2]

                phone = ""
                zipp = ""
                zip_index = -1
                state = ""

                country_code = "US"
                for str_data in address_list:
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(str_data))
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(str_data))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(str_data))
                    state_list = re.findall(r' ([A-Z]{2}) ', str_data)
                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        zip_index = address_list.index(str_data)
                        country_code = "US"

                    if ca_zip_list:
                        zipp = ca_zip_list[-1]
                        zip_index = address_list.index(str_data)
                        country_code = "CA"

                    if state_list:
                        state = state_list[-1]

                    if phone_list:
                        phone = phone_list[0].replace(")", "").replace("(", "")

                # logger.info("address_list === "+ str(address_list))
                street_address = address_list[zip_index - 1]#.split(",")[0]
                city = address_list[zip_index].split(",")[0]

                hours_index = [i for i, s in enumerate(address_list) if 'Hours:' in s]
                distance_index = [i for i, s in enumerate(address_list) if 'Distance:' in s]

                if hours_index:
                    if distance_index:
                        hours_of_operation = " ".join(address_list[hours_index[0] + 1:distance_index[0]])
                    else:
                        hours_of_operation = " ".join(address_list[hours_index[0] + 1:-1])

                latitude = ""
                longitude = ""
                split_lat_lng = ""
                if len(soup_locations.text.split("</span><br />"+street_address)) > 1:
                    split_lat_lng = soup_locations.text.split("</span><br />"+street_address)[1].split("],")[0].split(",")
                    if split_lat_lng:
                        latitude = split_lat_lng[1]
                        longitude = split_lat_lng[2]

                # logger.info("geo == " + str(split_lat_lng))
                # logger.info("street_address == " + str(hours_of_operation))

                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if store[2] + store[-3] in addresses:
                    continue

                addresses.append(store[2] + store[-3])
                store = [x.strip() if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store
            if current_results_len < MAX_RESULTS:
                # logger.info("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif current_results_len == MAX_RESULTS:
                # logger.info("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        except:
            continue
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
