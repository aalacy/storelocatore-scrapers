# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "abcfws.com"
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

    search_url = "https://www.abcfws.com/ccstoreui/v1/pages/layout/stores?ccvp=lg"
    stores_req = session.get(search_url, headers=headers)
    regions = json.loads(stores_req.text)["regions"]
    for region in regions:
        if "widgets" in region:
            widgets = region["widgets"]
            for wid in widgets:
                if "All Stores List" == wid["instanceName"]:
                    stores = json.loads(
                        "{"
                        + wid["templateSrc"]
                        .split("value: {")[1]
                        .strip()
                        .split("} --><!-- /ko -->")[0]
                        .strip()
                    )
                    for key, val in stores.items():
                        if "richText" in stores[key]:
                            url_sel = lxml.html.fromstring(
                                stores[key]["richText"]["content"]
                            )
                            slug = "".join(url_sel.xpath("//p/a/@href")).strip()
                            page_url = "https://www.abcfws.com" + slug
                            api_url = (
                                "https://www.abcfws.com/ccstoreui/v1/pages"
                                + slug
                                + "?dataOnly=false&cacheableDataOnly=true&productTypesRequired=true"
                            )

                            store_resp = session.get(api_url, headers=headers)
                            store_json = json.loads(store_resp.text)["data"]["page"][
                                "product"
                            ]

                            locator_domain = website

                            location_name = store_json["displayName"]
                            if location_name == "":
                                location_name = "<MISSING>"

                            street_address = store_json["addressLine1"]
                            city = store_json["city"]
                            state = store_json["state"]
                            zip = store_json["zipcode"]

                            country_code = store_json["countryCode"]

                            if street_address == "":
                                street_address = "<MISSING>"

                            if city == "":
                                city = "<MISSING>"

                            if state == "":
                                state = "<MISSING>"

                            if zip == "":
                                zip = "<MISSING>"

                            store_number = store_json["storeNumber"]
                            phone = store_json["phone1"]

                            location_type = "<MISSING>"

                            hours_of_operation = " ".join(
                                lxml.html.fromstring(store_json["openingHours"])
                                .text_content()
                                .split("\n")
                            )

                            latitude = store_json["latitude"]
                            longitude = store_json["longtitude"]

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
