# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "ctshirts.co.uk"
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
    loc_list = []

    search_url = "https://liveapi.yext.com/v2/accounts/me/locations?api_key=74daf99313eb1189e461442a605c448b&v=20071001&limit=50&offset={}"
    offset = 0
    while True:
        final_url = search_url.format(str(offset))
        stores_req = session.get(final_url, headers=headers)
        json_data = json.loads(stores_req.text)
        if json_data["response"]["count"] < offset:
            break

        stores = json_data["response"]["locations"]
        for store in stores:
            if (
                store["countryCode"] != "GB"
                and store["countryCode"] != "US"
                and store["countryCode"] != "CA"
            ):
                continue

            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["locationName"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]
            if "address2" in store:
                if store["address2"] is not None and len(store["address2"]) > 0:
                    street_address = street_address + ", " + store["address2"]

            city = store["city"]
            state = "<MISSING>"
            country_code = store["countryCode"]
            if "isoRegionCode" in store and (
                country_code == "US" or country_code == "CA"
            ):
                state = store["isoRegionCode"]
            zip = store["zip"]

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            store_number = store["id"]
            phone = store["phone"]

            location_type = "open"

            if "closed" in store:
                if store["closed"]["isClosed"] is True:
                    location_type = "closed"

            hours = store["hours"]
            hours_of_operation = ""
            hours_list = []
            if len(hours) > 0:
                hours = hours.split(",")
                for index in range(0, len(hours) - 1):
                    day_val = hours[index].split(":")[0].strip()
                    day = ""
                    if day_val == "1":
                        day = "Monday:"
                    if day_val == "2":
                        day = "Tuesday:"
                    if day_val == "3":
                        day = "Wednesday:"
                    if day_val == "4":
                        day = "Thursday:"
                    if day_val == "5":
                        day = "Friday:"
                    if day_val == "6":
                        day = "Saturday:"
                    if day_val == "7":
                        day = "Sunday:"

                    time = hours[index].split(":", 1)[1].strip().split(":")
                    time = time[0] + ":" + time[1] + "-" + time[2] + ":" + time[3]
                    hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["yextDisplayLat"]
            longitude = store["yextDisplayLng"]

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

        offset = offset + 50
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
