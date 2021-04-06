# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "kidskare.net"
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

    search_url = "https://kidskare.net/locations.php?n=4&id=4"
    stores_req = session.get(search_url, headers=headers)
    json_text = (
        stores_req.text.split("var infoWindowContent = ")[1]
        .strip()
        .split("]];")[0]
        .strip()
        + "]]"
    )

    markers = (
        stores_req.text.split("var markers = ")[1].strip().split("]];")[0].strip()
        + "]]"
    ).split("['")
    stores = json_text.split("['")
    for index in range(1, len(stores)):
        store_data = stores[index].split("'],")[0].strip()
        store_sel = lxml.html.fromstring(store_data)
        page_url = store_sel.xpath('//div[@class="info_content"]/p/a/@href')
        if len(page_url) > 0:
            page_url = page_url[0]
        else:
            page_url = "<MISSING>"

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="info_content"]/h1/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = "".join(
            store_sel.xpath('//div[@class="info_content"]/p/text()[1]')
        ).strip()
        street_address = address.split(",")[0].strip()
        city = address.rsplit(",")[1].strip()
        state = address.split(",")[2].strip().split(" ")[0].strip()
        zip = (
            address.split(",")[2].strip().split(" ")[1].strip().replace("'", "").strip()
        )

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

        store_number = "<MISSING>"
        phone = "".join(
            store_sel.xpath(
                '//div[@class="info_content"]//a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        location_type = "<MISSING>"
        map_link = markers[index]
        latitude = map_link.split("',")[1].split(",")[0].strip()
        longitude = map_link.split("',")[1].split(",")[1].strip().split("]")[0].strip()

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

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
