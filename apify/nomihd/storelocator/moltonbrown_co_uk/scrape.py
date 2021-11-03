# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "moltonbrown.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.moltonbrown.com/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
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

    search_url = "https://api.cxur-kaocorpor1-p3-public.model-t.cc.commerce.ondemand.com/kaowebservices/v2/moltonbrown-us/kao/stores"

    stores_req = session.get(search_url, headers=headers)
    kaoStores = json.loads(stores_req.text)["kaoStores"]
    for kaostr in kaoStores:
        country_code = kaostr["country"]
        if (
            "United States" == country_code
            or "Canada" == country_code
            or "United Kingdom" == country_code
        ):
            store_types = kaostr["stores"]
            for typ in store_types:
                if "Molton Brown Stores" == typ["storeType"]:
                    stores = typ["stores"]
                    for store in stores:
                        log.info(f"Pulling data for ID: {store}")
                        store_req = session.get(
                            "https://api.cxur-kaocorpor1-p3-public.model-t.cc.commerce.ondemand.com/kaowebservices/v2/moltonbrown-us/stores/"
                            + store,
                            headers=headers,
                        )

                        store_json = json.loads(store_req.text)
                        page_url = (
                            "https://www.moltonbrown.com/store/store-finder/"
                            + store_json["url"]
                        )
                        store_number = "<MISSING>"
                        latitude = store_json["geoPoint"]["latitude"]
                        longitude = store_json["geoPoint"]["longitude"]

                        location_name = store_json["name"]

                        locator_domain = website

                        location_type = store_json["storeType"]

                        street_address = store_json["address"]["line1"]
                        if "line2" in store_json["address"]:
                            if (
                                store_json["address"]["line2"] is not None
                                and len(store_json["address"]["line2"]) > 0
                            ):
                                street_address = (
                                    street_address
                                    + ", "
                                    + store_json["address"]["line2"]
                                )

                        city = store_json["address"]["town"]
                        state = "<MISSING>"
                        zip = store_json["address"]["postalCode"]
                        phone = store_json["address"]["phone"]
                        hours_of_operation = ""
                        hours_list = []
                        hours = store_json["kaoOpeningHoursList"]
                        for hour in hours:
                            day = hour["day"]
                            time = hour["openingTime"]
                            hours_list.append(day + ":" + time)

                        hours_of_operation = "; ".join(hours_list).strip()

                        if store_number == "":
                            store_number = "<MISSING>"

                        if location_name == "":
                            location_name = "<MISSING>"

                        if street_address == "" or street_address is None:
                            street_address = "<MISSING>"

                        if city == "" or city is None:
                            city = "<MISSING>"

                        if state == "" or state is None:
                            state = "<MISSING>"

                        if zip == "" or zip is None:
                            zip = "<MISSING>"

                        if country_code == "" or country_code is None:
                            country_code = "<MISSING>"

                        if phone == "" or phone is None:
                            phone = "<MISSING>"

                        if latitude == "" or latitude is None:
                            latitude = "<MISSING>"
                        if longitude == "" or longitude is None:
                            longitude = "<MISSING>"

                        if hours_of_operation == "":
                            hours_of_operation = "<MISSING>"

                        if location_type == "":
                            location_type = "<MISSING>"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
