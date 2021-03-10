# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "cbsbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "liveapi.yext.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
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

    offset = 0
    total = 1
    while offset < total:
        search_url = (
            "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=61f503dfe65522fe8c7a48d628b0740f"
            "&jsLibVersion=v1.6.3&sessionTrackingEnabled=true&"
            "input=location%20near%20me&experienceKey=cbs_answers&version="
            "PRODUCTION&filters=%7B%7D&facetFilters=%7B%7D&verticalKey="
            "Branches&limit=50&offset={}&locale=en&referrerPageUrl="
            "https%3A%2F%2Fwww.cbsbank.com%2F"
        )
        stores_req = session.get(search_url.format(str(offset)), headers=headers)

        json_data = json.loads(stores_req.text)
        stores = json_data["response"]["results"]
        total = json_data["response"]["resultsCount"]

        for store in stores:
            page_url = store["data"]["website"]

            locator_domain = website
            location_name = store["data"]["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["data"]["address"]["line1"]
            if "line2" in store["data"]["address"]:
                street_address = (
                    street_address + ", " + store["data"]["address"]["line2"]
                )

            city = store["data"]["address"]["city"]
            state = store["data"]["address"]["region"]
            zip = store["data"]["address"]["postalCode"]
            country_code = store["data"]["address"]["countryCode"]

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

            store_number = "<MISSING>"
            phone = store["data"]["mainPhone"]

            location_type = "<MISSING>"

            latitude = store["data"]["geocodedCoordinate"]["latitude"]
            longitude = store["data"]["geocodedCoordinate"]["longitude"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            hours = store["data"]["hours"]
            hours_list = []
            weekdays = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]

            for day in hours.keys():
                if day in weekdays:
                    if "openIntervals" in hours[day]:
                        time = (
                            hours[day]["openIntervals"][0]["start"]
                            + "-"
                            + hours[day]["openIntervals"][0]["end"]
                        )
                        hours_list.append(day + ":" + time)
                    else:
                        if hours[day]["isClosed"] is True:
                            hours_list.append(day + ":" + "Closed")

            hours_of_operation = "; ".join(hours_list).strip()

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
            loc_list.append(curr_list)

        offset = offset + 50

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
