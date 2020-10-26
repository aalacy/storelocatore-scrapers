import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('guess_ca')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/json;charset=UTF-8",
    }

    base_url = "https://www.guess.ca"

    while zip_code:
        result_coords = []

        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info("zip_code === " + zip_code)

        # zip_code = "96753"

        locations_url = "https://maps.stores.guess.com.prod.rioseo.com/api/getAsyncLocations?template=search&level=search&search="+str(zip_code)
        r_locations = request_wrapper(locations_url,"get", headers=headers)

        # logger.info("r_locations.text ==== " + r_locations.text)

        locations_json = r_locations.json()

        if locations_json["markers"] is None:

            if current_results_len < MAX_RESULTS:
                # logger.info("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif current_results_len == MAX_RESULTS:
                # logger.info("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")
            zip_code = search.next_zip()
            continue

        current_results_len = len(locations_json["markers"])  # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))

        locations_soup = BeautifulSoup(locations_json["maplist"],"lxml")
        # logger.info("locations_soup ~~~~~ "+ str(locations_soup.find("div",{"class":"tlsmap_list"}).text))
        locations_json = json.loads("["+locations_soup.find("div",{"class":"tlsmap_list"}).text[:-1]+"]")
        # logger.info("locations_json === "+ str(locations_json))
        for adr_json in locations_json:

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

            street_address = adr_json["address_1"]
            if "address_2" in adr_json and adr_json["address_2"]:
                street_address += " "+ adr_json["address_2"]
            city = adr_json["city"]
            # country_code = adr_json["countryCode"]
            state = adr_json["region"]
            zipp = adr_json["post_code"]
            # phone = adr_json["phoneNumber"]
            # store_number = adr_json["storeNumber"]
            phone = adr_json["local_phone"]
            latitude = adr_json["lat"]
            longitude = adr_json["lng"]
            location_type = adr_json["store_type_cs"]
            location_name = adr_json["location_name"]
            page_url = adr_json["url"]
            store_number = adr_json["fid"]
            hours_of_operation = ""

            hours_json = json.loads(adr_json["hours_sets:primary"])
            # logger.info("hours_json === " + str(hours_json))
            if "days" in hours_json:
                for days in hours_json["days"]:
                    hours_of_operation += " "+days +" "
                    # logger.info('hours_json["days"][days] === '+ str(type(hours_json["days"][days])))
                    if type(hours_json["days"][days]) is list:
                        for timing in hours_json["days"][days][0]:
                            # logger.info("timing === "+ str(hours_json["days"][days]))
                            hours_of_operation += timing +" : "+hours_json["days"][days][0][timing] +" "
                    else:
                        hours_of_operation += hours_json["days"][days]

                hours_of_operation = hours_of_operation.strip()

            # logger.info("hours_of_operation === "+ hours_of_operation)

            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))

            if ca_zip_list:
                country_code = "CA"

            if us_zip_list:
                country_code = "US"

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            if str(store[2]) not in addresses and country_code:
                addresses.append(str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

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
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
