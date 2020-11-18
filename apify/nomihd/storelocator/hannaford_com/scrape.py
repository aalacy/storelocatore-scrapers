# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
import json
from sglogging import sglog
import lxml.html

website = "hannaford.com"
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


def get_formated_street_address(street_address):

    if "&nbsp;" in street_address:
        add_before_nbsp = street_address.split("&nbsp;")[0].strip()
        if add_before_nbsp[0].isdigit():
            street_address = (
                street_address.split("&nbsp;")[0].strip().replace(",", "").strip()
            )
        else:
            add_after_nbsp = (
                street_address.split("&nbsp;")[1].strip().replace(",", "").strip()
            )
            if add_after_nbsp[0].isdigit():
                street_address = add_after_nbsp.replace("&nbsp;", " ").strip()
            else:
                street_address = street_address.replace("&nbsp;", " ").strip()

    return street_address


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

    sitemap_resp = session.get(
        "https://www.hannaford.com/sitemap/store_1.xml",
        headers=headers,
    )

    store_links = sitemap_resp.text.split("<loc>")
    for store in store_links:
        if "/locations/" in store:
            store_url = store.split("</loc>")[0].strip()
            store_resp = session.get(store_url, headers=headers)
            store_sel = lxml.html.fromstring(store_resp.text)
            json_data = json.loads(
                "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]' "/text()")
                )
            )

            location_name = json_data["name"]
            street_address = json_data["address"]["streetAddress"].strip()
            street_address = get_formated_street_address(street_address)

            city = json_data["address"]["addressLocality"]
            state = json_data["address"]["addressRegion"]
            zip = json_data["address"]["postalCode"]
            store_number = store_url.split("/")[-1].split("-")[-1].strip()
            location_type = json_data["@type"]
            if location_type == "":
                location_type = "<MISSING>"
            latitude = json_data["geo"]["latitude"]
            longitude = json_data["geo"]["longitude"]

            country_code = json_data["address"]["addressCountry"]
            if country_code == "":
                country_code = "<MISSING>"

            phone = json_data["telephone"]
            if phone == "":
                phone = "<MISSING>"
            page_url = store_url

            openingHoursSpecification = json_data["openingHoursSpecification"]
            hours_of_operation = ""
            for spec in openingHoursSpecification:
                opens = spec["opens"]
                closes = spec["closes"]
                if isinstance(spec["dayOfWeek"], list):
                    days_list = spec["dayOfWeek"]
                    for day in days_list:
                        hours_of_operation = (
                            hours_of_operation + day + ": " + opens + "-" + closes + " "
                        )
                else:
                    day = spec["dayOfWeek"]
                    hours_of_operation = (
                        hours_of_operation + day + ": " + opens + "-" + closes + " "
                    )
            hours_of_operation = hours_of_operation.strip()
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

            loc_list.append(curr_list)
            # break

    return loc_list


def scrape():
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
