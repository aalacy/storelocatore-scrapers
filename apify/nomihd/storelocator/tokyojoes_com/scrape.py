# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "tokyojoes.com"
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

    search_url = "https://tokyojoes.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = (
        stores_req.text.split("var markers_data = [")[1].strip().split("}];")[0].strip()
        + "},"
    )
    stores = stores.split("{")
    for index in range(1, len(stores)):
        store_data = stores[index].split("},")[0].strip()
        locator_domain = website
        latitude = store_data.split("lat:")[1].strip().split(",")[0].strip()
        longitude = store_data.split("lng:")[1].strip().split(",")[0].strip()
        store_number = store_data.split("id:")[1].strip().split(",")[0].strip()
        location_name = (
            store_data.split("title:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("'", "")
            .strip()
        )
        location_type = (
            store_data.split("is_upcoming:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("'", "")
            .strip()
        )
        if location_type == "1":
            location_type = "COMING SOON"

        store_sel = lxml.html.fromstring(
            store_data.split("html:")[1]
            .strip()
            .replace("'", "")
            .strip()
            .split("<strong>Phone:</strong>")[0]
            .strip()
        )
        raw_text = store_sel.xpath("//div/p/text()")
        add_list = []
        for text in raw_text:
            if len("".join(text)) > 0:
                add_list.append("".join(text))

        street_address = add_list[-2].strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()
        phone = (
            store_data.split("html:")[1]
            .strip()
            .split("<strong>Phone:</strong>")[1]
            .strip()
            .split("<br />")[0]
            .strip()
        )
        hours_of_operation = "; ".join(
            store_data.split("html:")[1]
            .strip()
            .split("<strong>Hours:</strong>")[1]
            .strip()
            .split("</p>")[0]
            .strip()
            .split("<br />")
        )
        html_sel = lxml.html.fromstring(
            store_data.split("html:")[1].strip().replace("'", "").strip()
        )
        page_url = "".join(
            html_sel.xpath('//div/a[contains(text(),"Order Online")]/@href')
        ).strip()

        if page_url == "http://order.tokyojoes.com/home/" or page_url == "":
            page_url = "<MISSING>"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
