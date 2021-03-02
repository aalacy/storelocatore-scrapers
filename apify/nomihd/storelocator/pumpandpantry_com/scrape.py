# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
import us

website = "pumpandpantry.com"
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

    search_url = "https://pumpandpantry.com/wp-admin/admin-ajax.php"

    data = {"action": "get_all_stores", "lat": "", "lng": ""}

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)

    for key in stores.keys():
        location_type = "<MISSING>"
        latitude = stores[key]["lat"]
        longitude = stores[key]["lng"]
        page_url = stores[key]["gu"]

        locator_domain = website
        location_name = stores[key]["na"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = stores[key]["st"]
        city = stores[key]["ct"].strip()
        state = ""
        phone = ""
        hours = []
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        sections = store_sel.xpath(
            '//div[@class="so-widget-sow-editor so-widget-sow-editor-base"]'
        )
        for sec in sections:
            if (
                "ADDRESS"
                in "".join(sec.xpath('h3[@class="widget-title"]/text()')).strip()
            ):

                address = sec.xpath(".//p/strong/text()")
                add_list = []
                for add in address:
                    if (
                        len("".join(add).strip()) > 0
                        and "Pump & Pantry" not in "".join(add).strip()
                    ):
                        add_list.append("".join(add).strip())

                if len(street_address) <= 0:
                    street_address = add_list[0].strip()

                try:
                    state = add_list[1].split(",")[-1].strip().split(" ")[0].strip()
                except:
                    pass

            if (
                "PHONE"
                in "".join(sec.xpath('h3[@class="widget-title"]/text()')).strip()
            ):

                phone = "".join(sec.xpath(".//p/strong/text()")).strip()

            if (
                "HOURS"
                in "".join(sec.xpath('h3[@class="widget-title"]/text()')).strip()
            ):

                hours = sec.xpath(".//p/strong/text()")

        zip = stores[key]["zp"]

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

        store_number = ""
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()
        hours_list = []
        # hours = store_sel.xpath(
        #     '//div[@class="store_locator_single_opening_hours"]/text()'
        # )
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
