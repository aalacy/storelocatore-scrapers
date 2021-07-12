# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import json

website = "sunglasshut.com/uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.sunglasshut.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=London%2C%20UK",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}
referUrl = "https://www.sunglasshut.com/uk/sunglasses/store-locations/map?location=London%2C%20UK"
fakeReq = session.get(referUrl, headers=headers)


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    search = static_coordinate_list(
        radius=100, country_code=SearchableCountries.BRITAIN
    )

    store_id_list = []
    for lat, long in search:
        log.info(f"{(lat, long)}")

        params = (
            ("latitude", lat),
            ("longitude", long),
            ("radius", "2000"),
        )

        stores_req = session.get(
            "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations",
            params=params,
        )
        log.info(f"Status Code: {stores_req}")
        stores = json.loads(stores_req.text)["locationDetails"]
        for store in stores:
            if store["countryCode"] == "GB":
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["displayAddress"]
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store["address"]

                city = store["city"]
                state = "<MISSING>"
                zip = store["zip"]
                country_code = store["countryCode"]

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                phone = store["phone"]
                location_type = "<MISSING>"

                store_number = store["id"]
                if store_number in store_id_list:
                    continue
                store_id_list.append(store_number)
                hours = store["hours"]
                hours_list = []
                for hour in hours:
                    day = hour["day"]
                    time = ""
                    if len(hour["open"]) <= 0 and len(hour["close"]) <= 0:
                        time = "Closed"
                    else:
                        time = hour["open"] + "-" + hour["close"]

                    hours_list.append(day + ":" + time)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

                latitude = store["latitude"]
                longitude = store["longitude"]
                if latitude == "" or latitude == "0.00000":
                    latitude = "<MISSING>"
                if longitude == "" or longitude == "0.00000":
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"

                curr_list = [
                    locator_domain,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
                yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
