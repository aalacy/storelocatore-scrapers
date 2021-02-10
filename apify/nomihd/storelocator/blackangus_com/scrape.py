# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "blackangus.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "api.momentfeed.com",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    url = (
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token"
        "=YFNPECMVZGRQCXJC&multi_account=false&page={}&pageSize=100"
    )
    page_no = 1
    while True:
        stores_req = session.get(
            url.format(str(page_no)),
            headers=headers,
        )
        stores = json.loads(stores_req.text)
        if "message" in stores:
            if stores["message"] == "No matching locations found":
                break

        for store in stores:
            locator_domain = website
            location_name = store["store_info"]["name"]
            street_address = store["store_info"]["address"]
            if len(store["store_info"]["address_extended"]) > 0:
                street_address = (
                    street_address + ", " + store["store_info"]["address_extended"]
                )
            city = store["store_info"]["locality"]
            state = store["store_info"]["region"]
            zip = store["store_info"]["postcode"]
            country_code = store["store_info"]["country"]
            page_url = "http://locations.blackangus.com" + store["llp_url"]
            phone = store["store_info"]["phone"]
            store_number = "<MISSING>"

            location_type = store["store_info"]["status"]
            if location_type == "":
                location_type = "<MISSING>"

            latitude = store["store_info"]["latitude"]
            longitude = store["store_info"]["longitude"]
            hours = store["store_info"]["store_hours"]
            hours_of_operation = ""
            if len(hours) > 0:
                hours = hours.split(";")
                for index in range(0, len(hours) - 1):
                    day_val = hours[index].split(",")[0].strip()
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

                    hours_of_operation = (
                        hours_of_operation
                        + day
                        + hours[index].split(",", 1)[1].replace(",", " - ").strip()
                        + " "
                    )

            hours_of_operation = hours_of_operation.strip()
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"

            if country_code == "":
                country_code = "<MISSING>"

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

        page_no = page_no + 1

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
