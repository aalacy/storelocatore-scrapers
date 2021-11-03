# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "foxandhound.com"
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

    search_url = "https://www.foxandhound.com/locations/index"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="locationLink"]/@href')
    for store_url in stores:
        page_url = "https://www.foxandhound.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        locID = (
            store_req.text.split('"locId":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        store_json = json.loads(
            session.get(
                "https://api.momentfeed.com/v1/lf/location/store-info/{}".format(locID)
            ).text
        )
        locator_domain = website
        location_name = store_json["name"]

        if location_name == "":
            location_name = "<MISSING>"

        street_address = store_json["address"]
        if (
            store_json["addressExtended"] is not None
            and len(store_json["addressExtended"]) > 0
        ):
            street_address = street_address + ", " + store_json["addressExtended"]

        city = store_json["locality"]
        state = store_json["region"]
        zip = store_json["postcode"]
        country_code = store_json["country"]

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

        phone = store_json["phone"]
        location_type = store_json["status"]
        store_number = "<MISSING>"

        hours_list = []
        if location_type == "open":
            hours = store_json["hours"].split(";")
            for index in range(0, len(hours) - 1):
                day_val = hours[index].split(",")[0].strip()
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

                hours_list.append(
                    day + hours[index].split(",", 1)[1].replace(",", " - ").strip()
                )

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        latitude = store_json["latitude"]
        longitude = store_json["longitude"]

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
