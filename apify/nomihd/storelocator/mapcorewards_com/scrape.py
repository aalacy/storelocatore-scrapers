# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "mapcorewards.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
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
        "https://mapco.modyo.cloud/api"
        "/content/spaces/stores/types/store/entries?per_page=100&page={}"
    )
    current_page = 1

    while True:
        stores_req = session.get(url.format(str(current_page)), headers=headers)

        json_data = json.loads(stores_req.text)

        if json_data["meta"]["current_page"] <= json_data["meta"]["total_pages"]:
            stores = json_data["entries"]
            for store in stores:
                locator_domain = website
                page_url = "https://www.mapcorewards.com/store/" + store["meta"]["slug"]

                raw_address = store["fields"]["address"][0]["location_street"]

                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                store_json = json.loads(
                    "".join(
                        store_sel.xpath('//script[@type="application/ld+json"]/text()')
                    ).strip(),
                    strict=False,
                )

                location_name = store_json["name"]
                if len(raw_address.split(",")) >= 4:
                    street_address = ", ".join(raw_address.rsplit(",")[:-3])
                    city = raw_address.split(",")[-3].strip()
                    try:
                        state = raw_address.split(",")[-2].strip().split(" ")[0].strip()
                    except:
                        state = store_json["address"]["addressRegion"]

                    try:
                        zip = raw_address.split(",")[-2].strip().split(" ")[1].strip()
                    except:
                        zip = store_json["address"]["postalCode"]

                else:
                    street_address = store_json["address"]["streetAddress"]
                    city = store_json["address"]["addressLocality"]
                    state = store_json["address"]["addressRegion"]
                    zip = store_json["address"]["postalCode"]

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "" or "United States" in city:
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "" or zip.isdigit() is False:
                    zip = "<MISSING>"
                country_code = store_json["address"]["addressCountry"]
                store_number = location_name.split(" ")[-1]
                if store_number == "":
                    store_number = "<MISSING>"

                phone = store_json["telephone"]
                location_type = store_json["@type"]
                latitude = store_json["geo"]["latitude"]
                longitude = store_json["geo"]["longitude"]
                hours_of_operation = ""
                hours = store_json["openingHoursSpecification"]
                for hour in hours:
                    hours_of_operation = hours_of_operation + (
                        hour["dayOfWeek"][0]
                        + ": "
                        + hour["opens"]
                        + "-"
                        + hour["closes"]
                        + " "
                    )

                hours_of_operation = hours_of_operation.strip()
                if location_type == "":
                    location_type = "<MISSING>"
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
        else:
            break

        current_page = current_page + 1

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
