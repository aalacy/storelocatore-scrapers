# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "olgas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "order.olgas.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "x-olo-request": "1",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "application/json, */*",
    "x-requested-with": "XMLHttpRequest",
    "x-olo-app-platform": "web",
    "__requestverificationtoken": "",
    "x-olo-viewport": "Desktop",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
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

    search_url = "https://www.olgas.com/wp-admin/admin-ajax.php?action=store_search&lat=42.36837&lng=-83.35271&max_results=50000&radius=50000&autoload=1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = store["url"]
        if page_url == "":
            page_url = "<MISSING>"
        locator_domain = website
        location_name = store["store"].replace("&#8211;", "-").strip()

        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        street_address = street_address.replace("Breeze Dining Court,", "").strip()
        city = store["city"]
        state = store["state"]
        zip = store["zip"]

        country_code = store["country"]
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
        hours_list = []
        if (
            store["store_time_weekdays"] is not None
            and len(store["store_time_weekdays"]) > 0
        ):
            hours_list.append("Mon-Sat:" + store["store_time_weekdays"])

        if (
            store["store_time_weekend"] is not None
            and len(store["store_time_weekend"]) > 0
        ):
            hours_list.append("Sun:" + store["store_time_weekend"])

        hours_of_operation = ""
        if len(hours_list) > 0:
            hours_of_operation = "; ".join(hours_list).strip()
        else:
            if page_url != "<MISSING>":
                log.info(page_url)
                store_req = session.get(
                    "https://order.olgas.com/api/vendors/"
                    + page_url.split("/menu/")[1].strip(),
                    headers=headers,
                )
                if "vendor" in store_req.text:
                    hours_sections = json.loads(store_req.text)["vendor"][
                        "weeklySchedule"
                    ]["calendars"]
                    for sec in hours_sections:
                        if "Business" == sec["scheduleDescription"]:
                            hours = sec["schedule"]
                            for hour in hours:
                                day = hour["weekDay"]
                                time = hour["description"]
                                hours_list.append(day + ":" + time)

                            break

                    hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["lat"]
        longitude = store["lng"]

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
