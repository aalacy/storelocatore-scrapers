# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "jeffersondentalclinics.com"
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

    search_url = "https://www.jeffersondentalclinics.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores_list = stores_sel.xpath('//ul[@class="all-city"]/li/a/@href')
    for store_url in stores_list:
        page_url = store_url

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')

        hours_of_operation = ""
        store_json = None
        for js in json_list:
            if "openingHours" in js:
                hours_of_operation = (
                    ";".join(
                        js.split('"openingHours": ')[1]
                        .strip()
                        .split('"contactPoint"')[0]
                        .strip()
                        .replace('",', "")
                        .replace('"', "")
                        .strip()
                        .split("\n")
                    )
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

                store_json = json.loads(
                    js.split('"openingHours": ')[0].strip()
                    + '"contactPoint"'
                    + js.split('"openingHours": ')[1]
                    .strip()
                    .split('"contactPoint"')[1]
                    .strip()
                )
                break

        if store_json is not None:
            locator_domain = website
            location_name = store_json["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store_json["address"]["streetAddress"].strip()
            city = store_json["address"]["addressLocality"].strip()
            state = (
                store_json["address"]["addressRegion"].strip().replace(",", "").strip()
            )
            zip = store_json["address"]["postalCode"].strip()

            if state.isdigit():
                zip = state
                state = "<MISSING>"

            country_code = store_json["address"]["addressCountry"]

            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zip == "" or zip is None:
                zip = "<MISSING>"

            temp_address = "".join(
                store_sel.xpath('//span[@class="location-address"]/text()')
            ).strip()
            if state == "<MISSING>":
                state = temp_address.split(",", 1)[1].strip().split(" ")[0].strip()
                if state.isdigit():
                    state = temp_address.split(",", 1)[0].strip().split(" ")[-1].strip()

            if city == "<MISSING>":
                city = temp_address.split(",")[1].strip().replace(state, "").strip()

            store_number = "<MISSING>"
            phone = store_json["contactPoint"]["telephone"]

            location_type = store_json["@type"]
            if location_type == "" or location_type is None:
                location_type = "<MISSING>"

            latitude = store_json["geo"]["latitude"]
            longitude = store_json["geo"]["longitude"]

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
