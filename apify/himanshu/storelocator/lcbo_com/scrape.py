import csv
import time

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



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
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 10
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    base_url = "https://www.lcbo.com"
    r_store_id = session.get(base_url, headers=headers)
    store_id = r_store_id.text.split('"storeId":\'')[1].split("'")[0]
    # print("store_id === " + str(store_id))

    while zip_code:
        result_coords = []

        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print("zip_code === " + zip_code)

        # zip_code = "P0V 2W0"

        data = 'citypostalcode=' + str(zip_code)
        location_url = "https://www.lcbo.com/webapp/wcs/stores/servlet/AjaxStoreLocatorResultsView?storeId=" + str(
            store_id)

        while True:
            try:
                r = session.post(location_url, headers=headers, data=data)
                break
            except Exception as e:
                # print("Error = "+ str(e))
                time.sleep(10)
                continue

        soup = BeautifulSoup(r.text, "lxml")

        # print("soup ==== "+ str(soup))

        current_results_len = len(
            soup.find_all("div", {"class": "row store-row"}))  # it always need to set total len of record.
        # print("current_results_len === " + str(current_results_len))

        for script in soup.find_all("div", {"class": "row store-row"}):

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

            store_number = script["data-store-num"]
            street_address = script["data-address"]
            city = script["data-city"]
            latitude = script["data-lat"]
            longitude = script["data-long"]
            location_name = script.find("div",{"class":"store-name"}).text.strip()
            phone = script.find("div",{"class":"store-phone"}).text.strip()
            zipp = script.find("div",{"class":"store-postal"}).text.strip()
            hours_json_str = "[{"+script.find("a",{"class":"md-mt-10 storehourslink"})["onclick"].split("[{")[1].split("}]")[0]+"}]"
            hours_json = json.loads(hours_json_str)

            if zipp.isdigit():
                country_code = "US"
            else:
                zipp = zipp[:3]+" "+zipp[3:]
                country_code = "CA"

            hours_of_operation = ""
            index = 1
            for hours_day in hours_json:
                hours_of_operation += hours_day[str(index)][0] +" "
                index += 1

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) not in addresses:
                addresses.append(str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
