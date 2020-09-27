import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests()
base_url = "https://www.searsauto.com"
log = sglog.SgLogSetup().get_logger(logger_name=base_url)


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    MAX_RESULTS = 20
    MAX_DISTANCE = 200
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=["US"])
    zip_code = search.next_zip()
    addressess = []

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-type": "application/json",
        "origin": "https://www.searsauto.com",
        "referer": "https://www.searsauto.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    }
    r = session.post("https://app.searsauto.com/sa-api/init", headers=headers)

    while zip_code:
        result_coords = []

        location_url = "https://app.searsauto.com/sa-api/stores/" + str(zip_code)
        log.debug(location_url)

        r = session.get(location_url, headers=headers)
        r.raise_for_status()
        r_json = r.json()

        json_data = r_json["autoStores"]

        for value in json_data:
            location_name = "Sears Auto Center at " + value["city"]
            street_address = value["address1"] + " " + value["address2"].strip()
            city = value["city"]
            state = value["state"]
            zipp = value["postalCode"]
            store_number = value["storeNumber"]
            phone = value["phone"]
            location_type = value["storeType"] + " - " + value["locationType"]
            latitude = value["latitude"]
            longitude = value["longitude"]
            hours_of_operation = value["hours"]
            time = ""
            for j in hours_of_operation:
                if "open" in j:
                    time = (
                        time + " " + j["dayOfWeek"] + " " + j["open"] + "-" + j["close"]
                    )

            page_url = "https://www.searsauto.com" + value["detailsUrl"]

            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(time.lower() if time.lower() else "<MISSING>")
            store.append(page_url)
            store = [
                x.encode("ascii", "ignore").decode("ascii").strip()
                if type(x) == str
                else x
                for x in store
            ]
            if store[2] in addressess:
                log.debug(f">>> already have {store[2]}")
                continue
            addressess.append(store[2])
            log.debug(store)
            yield store

        if len(json_data) < MAX_RESULTS:

            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:

            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)


scrape()
