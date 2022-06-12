# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "thecounter.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    loc_list = []

    locations_resp = session.get(
        "https://locator.kahalamgmt.com/locator/index.php?brand=32",
        headers=headers,
    )
    stores = locations_resp.text.split("Locator.stores[")
    for index in range(1, len(stores)):
        json_temp = stores[index].split("= ")[1].strip().split("Locator")[0].strip()

        store_json = json.loads(json_temp)
        location_name = store_json["Name"]
        street_address = store_json["Address"]
        city = store_json["City"]
        state = store_json["State"]
        if state == "":
            state = "<MISSING>"

        zip = store_json["Zip"]
        if zip == "":
            zip = "<MISSING>"

        location_type = store_json["StatusName"]
        if location_type == "":
            location_type = "<MISSING>"

        latitude = store_json["Latitude"]
        longitude = store_json["Longitude"]

        country_code = store_json["CountryCode"]
        if country_code == "IE":
            country_code = "GB"
        if country_code == "":
            country_code = "<MISSING>"

        store_number = str(store_json["StoreId"])
        phone = store_json["Phone"]

        if phone == "" or phone == "() -":
            phone = "<MISSING>"

        page_url = "https://www.thecounter.com/stores/" + store_number
        store_req = session.get(page_url, headers=headers)
        store_resp = json.loads(
            (
                store_req.text.split('type="application/ld+json">')[1]
                .strip()
                .split("</script>")[0]
                .strip()
            )
        )

        hours_of_operation = store_resp["openingHours"].replace(",", "").strip()

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

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
        if country_code == "US" or country_code == "CA" or country_code == "GB":
            loc_list.append(curr_list)
        # break
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
