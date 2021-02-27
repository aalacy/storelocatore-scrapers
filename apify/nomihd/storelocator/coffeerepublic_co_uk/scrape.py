# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
from lxml import etree
from sgscrape import sgpostal as parser
from bs4 import BeautifulSoup as BS

website = "coffeerepublic.co.uk"
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

    search_url = "https://coffeerepublic.co.uk/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t="
    stores_req = session.get(search_url, headers=headers)
    stores_sel = etree.fromstring(stores_req.text)
    stores = stores_sel.xpath("//store/item")
    for store in stores:
        page_url = ""
        locator_domain = website
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zip = ""
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        hours_of_operation = ""

        for child in store:
            if child.tag == "latitude":
                latitude = child.text
            if child.tag == "longitude":
                longitude = child.text
            if child.tag == "storeId":
                store_number = child.text
            if child.tag == "exturl":
                page_url = child.text
            if child.tag == "telephone":
                phone = child.text
            if child.tag == "location":
                location_name = child.text.replace("&amp;", "&").strip()
            if child.tag == "address":
                raw_address = child.text
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = "GB"

            if child.tag == "operatingHours":
                hours_of_operation = BS(
                    "; ".join(
                        child.text.replace("<b>", "")
                        .replace("</b>", ":")
                        .replace("<br>", "")
                        .split("\n")
                    )
                    .strip()
                    .replace("<br", ";")
                    .replace("style=", "<style="),
                    "html.parser",
                ).get_text()

                hours_of_operation = (
                    hours_of_operation.encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", ":")
                    .strip()
                )
        if location_name == "":
            location_name = "<MISSING>"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

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
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
