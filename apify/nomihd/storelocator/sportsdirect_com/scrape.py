# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "sportsdirect.com"
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

    search_url = "https://www.sportsdirect.com/stores/all"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="letItems"]')
    for store in stores:
        if "".join(store.xpath("@data-country-code")) == "GB":

            page_url = (
                "https://www.sportsdirect.com"
                + "".join(store.xpath("a/@href")).strip().replace("../", "/").strip()
            )
            locator_domain = website

            store_req = session.get(page_url, headers=headers)

            while "var store =" not in store_req.text:
                store_req = session.get(page_url, headers=headers)

            store_json = json.loads(
                store_req.text.split("var store =")[1].strip().split("};")[0].strip()
                + "}"
            )

            location_name = store_json["formattedStoreNameLong"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store_json["address"]
            city = store_json["town"]
            state = store_json["county"]
            zip = store_json["postCode"]
            country_code = store_json["countryCode"]

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

            store_number = str(store_json["code"])
            phone = store_json["telephone"]

            location_type = store_json["storeType"]

            hours = store_json["openingTimes"]
            hours_list = []
            for hour in hours:
                if hour["dayOfWeek"] == 0:
                    day = "Monday:"
                if hour["dayOfWeek"] == 1:
                    day = "Tuesday:"
                if hour["dayOfWeek"] == 2:
                    day = "Wednesday:"
                if hour["dayOfWeek"] == 3:
                    day = "Thursday:"
                if hour["dayOfWeek"] == 4:
                    day = "Friday:"
                if hour["dayOfWeek"] == 5:
                    day = "Saturday:"
                if hour["dayOfWeek"] == 6:
                    day = "Sunday:"

                if hour["openingTime"] is not None and hour["closingTime"] is not None:
                    time = hour["openingTime"] + "-" + hour["closingTime"]
                    hours_list.append(day + time)

            hours_of_operation = ";".join(hours_list).strip()
            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

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
