# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

website = "bestwayrto.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
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
    search_url = "https://www.bestwayrto.com/wp-admin/admin-ajax.php"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=25,
    )

    data = {
        "address": "",
        "formdata": "addressInput=",
        "name": "",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "none",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "1",
        "options[initial_radius]": "500",
        "options[label_directions]": "",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax: ",
        "options[label_phone]": "Phone: ",
        "options[label_website]": "View Store Page",
        "options[loading_indicator]": "",
        "options[map_center]": "United States",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "https://www.bestwayrto.com/wp-content/plugins/store-locator-le/images/icons/bulb_purple-dot.png",
        "options[map_home_icon]": "https://www.bestwayrto.com/wp-content/plugins/store-locator-le/images/icons/blank.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[message_bad_address]": "Could not locate this address. Please try a different location.",
        "options[message_no_results]": "No locations found.",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "0",
        "options[zoom_level]": "9",
        "options[zoom_tweak]": "1",
        "radius": "50",
        "tags": "",
        "action": "csl_ajax_onload",
    }
    for lat, long in search:
        log.info(f"{(lat, long)} | remaining: {search.items_remaining()}")
        data["lat"] = lat
        data["lng"] = long
        data["options[map_center_lat]"] = lat
        data["options[map_center_lng]"] = long

        stores_req = session.post(search_url, data=data, headers=headers)
        stores = json.loads(stores_req.text)["response"]

        for store in stores:

            latitude = store["lat"]
            longitude = store["lng"]

            search.found_location_at(latitude, longitude)

            page_url = "<MISSING>"

            locator_domain = website
            location_name = store["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]
            if store["address2"] is not None and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]
            city = store["city"]
            state = store["state"]
            zip = store["zip"]

            country_code = "<MISSING>"

            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zip == "" or zip is None:
                zip = "<MISSING>"

            store_number = str(store["id"])
            phone = store["phone"]

            location_type = "<MISSING>"
            hours_of_operation = store["hours"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            if hours_of_operation == "" or hours_of_operation is None:
                hours_of_operation = "<MISSING>"

            if phone == "" or phone is None:
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
