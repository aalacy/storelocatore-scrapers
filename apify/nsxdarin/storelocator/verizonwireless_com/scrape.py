import csv
from sgrequests import SgRequests
from sgzip import *
from typing import *
import json
from concurrent.futures import *
from sglogging import sglog
import time

MISSING = '<MISSING>'
website = 'verizonwireless.com'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
SEARCH_RADIUS_MILES = 2
paralellism = 15
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def request_with_retries(url):
    return session.get(url, headers=headers)

def parse_store_locations(iter_lines: Iterator):
    for b_line in iter_lines:
        line = str(b_line)
        if "var searchJSON" in line:
            json_starts = line.find("[")
            json_ends = line.rfind("]") + 1
            json_str = line[json_starts:json_ends].strip().replace("\\","") # we don't care about escape chars

            try:
                return json.loads(json_str)
            except json.decoder.JSONDecodeError:
                if json_str:
                    log.info(f"Cannot parse string to json (most likely due to 'no results' javascript) : {json_str}")
                return []

    log.debug("Found no store locations in resultset")
    return []

def get(record: Dict[str, str], key: str):
    try:
        value = record[key]
        if isinstance(value, list):
            v_strip = [item.strip() for item in value if item.strip]
            return ", ".join(v_strip) if v_strip else MISSING
        elif isinstance(value, dict):
            v_strip = [f"{k.strip()}: {v.strip()}" for k, v in value.items() if k.strip() ]
            return ", ".join(v_strip) if v_strip else MISSING
        elif isinstance(value, str):
            v_strip = value.strip()
            return v_strip if v_strip else MISSING
        else:
            log.error(f"Unknown record type: {key} in {record}")
            raise ValueError(f"Unknown record type: {key} in {record}")

    except KeyError:
        return MISSING

def populate_records(r) -> list:
    json_results = parse_store_locations(r.iter_lines())

    for j_result in json_results:
        page_url = f"https://www.verizonwireless.com{j_result['storeUrl']}"
        store_name = get(j_result, 'storeName')
        address = get(j_result, 'address')
        city = get(j_result, 'city')
        state = get(j_result, 'state')
        zipcode = get(j_result, 'zip')
        country = 'US'
        store_number = get(j_result, 'storeNumber')
        phone = get(j_result, 'phone')
        store_type = get(j_result, 'typeOfStore')
        lat = get(j_result, 'lat')
        lng = get(j_result, 'lng')
        hours = get(j_result, 'openingHours')

        yield [website, page_url, store_name, address, city, state, zipcode, country, store_number, phone,
               store_type, lat, lng, hours]

def fetch_data_for_coord(coord: Tuple[float, float]):
    (lat, long) = (coord[0], coord[1])
    url = f'https://www.verizonwireless.com/stores/storesearchresults/?lat={lat}&long={long}'
    return request_with_retries(url)

def fetch_data():
    all_search_coords = sgzip.coords_for_radius(SEARCH_RADIUS_MILES, SearchableCountries.USA)
    ids = set()
    with ThreadPoolExecutor(max_workers=paralellism, thread_name_prefix='fetcher') as executor:
        for raw_result in executor.map(fetch_data_for_coord, all_search_coords):
            for res in populate_records(raw_result):
                store_number = res[8]
                if store_number in ids:
                    continue
                else:
                    ids.add(store_number)

                yield res

                len_ids = len(ids)
                if len_ids % 100 == 0:
                    log.debug(f"Counted {len_ids} so far...")

def scrape():
    start = time.time()
    data = fetch_data()
    write_output(data)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")

if __name__ == "__main__":
    scrape()
