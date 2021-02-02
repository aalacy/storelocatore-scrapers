# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from lxml import etree

website = "malvernschool.com"
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

    search_url = "https://malvernschool.com/wp-content/plugins/malvern-maps/js/phpsqlsearch_genxml-active.php?lat=39.9111323&lng=-75.4927278&radius=10000"
    stores_req = session.get(search_url, headers=headers)
    store_xml = etree.fromstring(stores_req.text)
    markers = store_xml.xpath("//markers/marker")
    for marker in markers:
        locator_domain = website
        location_type = "<MISSING>"

        page_url = marker.attrib["link"]
        log.info(page_url)
        latitude = marker.attrib["lat"]
        longitude = marker.attrib["lng"]
        store_number = marker.attrib["postId"]
        location_name = marker.attrib["name"]

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        street_address = "".join(
            store_sel.xpath(
                '//div[@class="location-single-address-container"]/div[@class="location-single-address street"]/text()'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@class="location-single-address-container"]/div[@class="location-single-address city"]/text()'
            )
        ).strip()
        if "," == city[-1]:
            city = "".join(city[:-1]).strip()

        state = "".join(
            store_sel.xpath(
                '//div[@class="location-single-address-container"]/div[@class="location-single-address state"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//div[@class="location-single-address-container"]/div[@class="location-single-address zip"]/text()'
            )
        ).strip()

        phone = (
            "".join(
                store_sel.xpath(
                    '//div[@class="location-single-address-container"]/div[@class="location-single-address phone"]/text()'
                )
            )
            .strip()
            .replace("Ph:", "")
            .strip()
        )
        hours = store_sel.xpath('//div[@class="hours"]/text()')
        hours_list = []
        hours_of_operation = ""
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                if "*Hours may differ due to COVID-19" == "".join(hour).strip():
                    continue
                elif "*This location is temporarily closed." == "".join(hour).strip():
                    location_type = "temporarily closed"
                else:
                    hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()

        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

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

        if location_type == "":
            location_type = "<MISSING>"

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
