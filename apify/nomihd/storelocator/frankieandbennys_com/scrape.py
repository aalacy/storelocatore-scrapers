# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "frankieandbennys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
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
    url_list = []

    search_url = "https://www.frankieandbennys.com/sitemap.xml"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        if "https://www.frankieandbennys.com/restaurants/" in stores[index]:
            slug = (
                stores[index]
                .split("https://www.frankieandbennys.com/restaurants/")[1]
                .strip()
                .split("/")[0]
                .strip()
            )
            url_list.append(slug)

    stores = list(set(url_list))
    for slug in stores:
        page_url = "https://www.frankieandbennys.com/restaurants/" + slug
        if (
            "https://www.frankieandbennys.com/restaurants/east-midlands-airport"
            == page_url
        ):
            continue
        log.info(page_url)
        store_req = session.get(
            "https://www.frankieandbennys.com/api/content/restaurants/" + slug
        )
        if "restaurant" in store_req.text:
            store_json = json.loads(store_req.text)["restaurant"]["fields"]
            latitude = ""
            longitude = ""
            if "latitude" in store_json:
                latitude = store_json["latitude"]
                longitude = store_json["longitude"]

            location_name = ""
            if "title" in store_json:
                location_name = store_json["title"]

            locator_domain = website

            location_type = "<MISSING>"

            street_address = ""
            if "street" in store_json:
                street_address = store_json["street"]

            if (
                "additional" in store_json
                and store_json["additional"] is not None
                and len(store_json["additional"]) > 0
            ):
                street_address = street_address + ", " + store_json["additional"]

            city = ""
            state = ""
            zip = ""
            country_code = ""
            phone = ""
            if "city" in store_json:
                city = store_json["city"]
            if "region" in store_json:
                state = store_json["region"]
            if state == "Northern Ireland":
                continue
            if "postalCode" in store_json:
                zip = store_json["postalCode"]
            if "country" in store_json:
                country_code = store_json["country"]

            if "telephone" in store_json:
                phone = store_json["telephone"]

            if "," in city:
                city = city.split(",")[0].strip()

            hours_of_operation = ""
            hours_list = []
            for key in store_json.keys():
                if (
                    "openM" in key
                    or "openT" in key
                    or "openW" in key
                    or "openT" in key
                    or "openF" in key
                    or "openS" in key
                ):
                    time = store_json[key]
                    day = key.replace("open", "").strip()
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = "<MISSING>"
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
            yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
