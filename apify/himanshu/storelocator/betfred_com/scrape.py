import csv
import sgzip
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('betfred_com')



locator_domain = "https://www.betfred.com/"
MAX_DISTANCE = 5
url = "https://www.betfred.com/services/gis/searchstores"

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def process_locations(ids: set, result_coords, locations):
    current_results_len = len(locations)
    for loc in locations:
        store_number = loc["ShopNumber"]
        location_name = loc["Title"]
        if len(loc["Address"].split(",")) > 1:
            street_address = " ".join(loc["Address"].split(",")[:-1]).strip()
            city = loc["Address"].split(",")[-1].strip()
        elif len(loc["Address"].split("  ")) > 1:

            # Berryden Retail Park  Berryden
            street_address = " ".join(loc["Address"].split("  ")[:-1]).strip()
            city = loc["Address"].split("  ")[-1]
        else:
            street_address = loc["Address"]
            city = "<MISSING>"
        state = "<MISSING>"
        zipp = loc["Postcode"]
        country_code = "UK"
        phone = "<MISSING>"
        latitude = loc["Location"]["Latitude"]
        longitude = loc["Location"]["Longitude"]
        hours_of_operation = loc["OpeningHoursDescription"].replace("\r\n", "").strip()
        location_type = "<MISSING>"
        page_url = "https://www.betfred.com/shop-locator"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        result_coords.append((latitude, longitude))
        if store_number not in ids:
            ids.add(store_number)
            yield [x if x else "<MISSING>" for x in store]

def http_req(coord):
    coord_query = ','.join([str(coord[0]), str(coord[1])])
    payload = "{\"SearchLocation\":\"" + coord_query + "\",\"MaximumShops\":10,\"MaximumDistance\":5}"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
        'Accept': "*/*",
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "3c1ecc49-46ce-46e0-9b1e-fdbe4cc065f2,fe8dde9f-a9f4-4533-93bc-31dc8ea517fa",
        'Host': "www.betfred.com",
        'Accept-Encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    return SgRequests().requests_retry_session().post(url, data=payload, headers=headers)


def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    ids = set()
    retries = []

    while coord:
        result_coords = []
        response = http_req(coord)
        try:
            locations = response.json()['Stores']
            for record in process_locations(ids, result_coords, locations):
                yield record
        except Exception as e:
            logger.info(f"Error on record parse/process; will retry later. Err: {e}")
            logger.info(response.text)
            retries.append(coord)
            continue

        if current_results_len == 0:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        else:
            # logger.info("max count update")
            search.max_count_update(result_coords)

        coord = search.next_coord()

    for coord in retries:
        response = http_req(coord)
        try:
            locations = response.json()['Stores']
            for record in process_locations(ids, [], locations):
                yield record
        except Exception as e:
            logger.info(f"Second error on record parse/process: {e}")
            logger.info(response.text)


def scrape():
    data = fetch_data()
    write_output(data)

if __name__ == "__main__":
    scrape()
