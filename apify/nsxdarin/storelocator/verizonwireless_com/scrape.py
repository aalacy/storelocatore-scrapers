import csv
from sgrequests import SgRequests
import sgzip
from tenacity import retry, stop_after_attempt
from typing import *
import json

search = sgzip.ClosestNSearch()
search.initialize()

MISSING = '<MISSING>'

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

MAX_RESULTS = 250
MAX_DISTANCE = 5

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

@retry(stop=stop_after_attempt(7))
def request_with_retries(url):
    session = SgRequests()
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
                print(f"Cannot parse string to json (most likely due to 'no results' javascript) : {json_str}")
                return []

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
            raise ValueError(f"Unknown record type: {key} in {record}")

    except KeyError:
        return MISSING


def fetch_data():
    ids = set()
    coord = search.next_coord()
    while coord:
        x = coord[0]
        y = coord[1]
        website = 'verizonwireless.com'
        url = f'https://www.verizonwireless.com/stores/storesearchresults/?lat={x}&long={y}'
        r = request_with_retries(url)
        result_coords = []

        json_results = parse_store_locations(r.iter_lines())

        for j_result in json_results:
            page_url = 'https://www.verizonwireless.com' + j_result['storeUrl']
            if page_url in ids:
                continue
            else:
                ids.add(page_url)

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

            result_coords.append((lat, lng))

            yield [website, page_url, store_name, address, city, state, zipcode, country, store_number, phone, store_type, lat, lng, hours]

        if len(result_coords) < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif len(result_coords) == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

if __name__ == "__main__":
    scrape()