# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
import us

website = "chickenshack.com"
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

    search_url = "https://chickenshack.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    json_text = (
        "".join(stores_sel.xpath('//script[@id="maplistko-js-extra"]/text()'))
        .strip()
        .rsplit(";", 1)[0]
        .strip()
        .split("var maplistScriptParamsKo =")[1]
        .strip()
    )
    stores = json.loads(json_text)["KOObject"][0]["locations"]

    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        address = (
            store["address"]
            .replace("<p>", "")
            .strip()
            .replace("</p>", "")
            .strip()
            .replace("<br />", "")
            .strip()
        )
        try:
            address = address.split("United States")[0].strip()
        except:
            pass

        try:
            address = address.split(", USA")[0].strip()
        except:
            pass

        address = address.split("\n")
        street_address = address[0].strip()
        city = address[1].strip().split(",")[0].strip()
        state = address[1].strip().split(",")[-1].strip()
        zip = address[2].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"
        else:
            add_from_desc = (
                store["description"]
                .split("<strong>Address:</strong>")[1]
                .strip()
                .split("<")[0]
                .strip()
            )
            state = add_from_desc.split(",")[-1].strip().split(" ")[0].strip()
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

        store_number = "<MISSING>"
        phone = ""
        try:
            phone = (
                store["simpledescription"]
                .split("<p><strong>Phone:</strong>")[1]
                .strip()
                .split(">")[1]
                .strip()
                .split("</a>")[0]
                .strip()
                .replace("</a", "")
                .strip()
            )
        except:
            pass

        location_type = "<MISSING>"
        hours_of_operation = ""
        hours_list = []
        try:
            hours = (
                store["simpledescription"]
                .split("Hours:")[1]
                .strip()
                .split("<strong>")[0]
                .strip()
                .replace("<br />", "")
                .strip()
                .replace("</strong>", "")
                .replace("<p>", "")
                .replace("</p>", "")
                .split("\n")
            )
            for hour in hours:
                if (
                    len("".join(hour).strip()) > 0
                    and "DRIVE-THRU ONLY" not in hour
                    and "Closed Labor Day" not in hour
                ):
                    hours_list.append("".join(hour).strip())
        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["latitude"]
        longitude = store["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
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
