# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import json

website = "sourceforsports.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
}


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
    loc_list = []

    search_url = "https://www.sourceforsports.com/api/stores/GetStoresLocatorResult?lat={}&lng={}&range=800&rand=8"
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    ID_list = []
    for lat, lng in coords:
        stores_req = session.get(search_url.format(lat, lng), headers=headers)
        stores_json = json.loads(
            stores_req.text.replace('\\"', '"')
            .replace("\\r\\n", "")
            .strip()
            .replace('"{', "{")
            .replace('}"', "}")
        )
        if "store" in stores_json:
            stores = stores_json["store"]
            for store in stores:
                store_number = store["StoreId"]
                if store_number not in ID_list:
                    ID_list.append(store_number)
                    log.info(f"Pulling data for store ID: {store_number}")
                    store_req = session.get(
                        "https://www.sourceforsports.com/api/stores/GetStoreDetail?storeid="
                        + store_number,
                        headers=headers,
                    )
                    store = store_req.json()

                    page_url = (
                        "https://www.sourceforsports.com/en-US/Stores/" + store["Url"]
                    )
                    locator_domain = website
                    location_name = store["StoreName"]

                    if location_name == "":
                        location_name = "<MISSING>"

                    street_address = store["Address"]

                    city = store["City"]
                    state = store["Province"]
                    zip = store["PostalCode"]

                    country_code = store["Country"]

                    if country_code == "":
                        country_code = "<MISSING>"

                    if street_address == "":
                        street_address = "<MISSING>"

                    if city == "":
                        city = "<MISSING>"

                    if state == "":
                        state = "<MISSING>"

                    if zip == "":
                        zip = "<MISSING>"

                    phone = store["LocalPhone"]

                    location_type = "<MISSING>"
                    if store["StoreHours"] is not None and len(store["StoreHours"]) > 0:
                        hours_sel = lxml.html.fromstring(store["StoreHours"])
                        hours = hours_sel.xpath(".//text()")
                        hours_list = []
                        for hour in hours:
                            if len("".join(hour).strip()) > 0:
                                hours_list.append("".join(hour).strip())

                    hours_of_operation = (
                        "; ".join(hours_list)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )

                    latitude = store["Latitude"]
                    longitude = store["Longitude"]
                    if latitude == "":
                        latitude = "<MISSING>"
                    if longitude == "":
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
                    loc_list.append(curr_list)
            # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
