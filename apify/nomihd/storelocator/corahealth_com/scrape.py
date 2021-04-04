# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "corahealth.com"
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

    search_url = "https://www.coraphysicaltherapy.com/wpsl_stores-sitemap.xml"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        page_url = "".join(stores[index].split("</loc>")[0].strip()).strip()
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        store_json = None
        store_json = json.loads(
            store_sel.xpath('//script[@type="application/ld+json"]/text()')[-1]
        )

        if store_json:
            locator_domain = website
            location_name = store_json["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store_json["address"]["streetAddress"]
            city = store_json["address"]["addressLocality"]
            state = store_json["address"]["addressRegion"]
            zip = store_json["address"]["postalCode"]
            country_code = store_json["address"]["addressCountry"]

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            if country_code == "":
                country_code = "<MISSING>"

            store_number = "<MISSING>"
            phone = store_json["telephone"]

            location_type = store_json["@type"]
            hours = store_json["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hours:
                day = hour["dayOfWeek"][0]
                time = hour["opens"] + "-" + hour["closes"]
                hours_of_operation = hours_of_operation + day + ":" + time + " "

            hours_of_operation = hours_of_operation.strip()

            latitude = store_json["geo"]["latitude"]
            longitude = store_json["geo"]["longitude"]

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
