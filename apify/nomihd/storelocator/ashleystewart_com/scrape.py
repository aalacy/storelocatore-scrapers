# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "ashleystewart.com"
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

    search_url = "https://www.ashleystewart.com/stores/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="store-information-div"]')
    for store in stores:
        page_url = (
            "https://www.ashleystewart.com"
            + "".join(store.xpath('div[@class="store-detail"]/a/@href')).strip()
        )

        locator_domain = website
        location_name = "".join(
            store.xpath('div[@class="store-name"]/a/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        address = store.xpath('div[@class="store-address"]/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city = add_list[1].strip().split(",")[0].strip()
        state = " ".join(
            " ".join(add_list[1].split("\n"))
            .strip()
            .split(",")[1]
            .strip()
            .rsplit(" ", 1)[0:-1]
        ).strip()
        zip = (
            " ".join(add_list[1].split("\n"))
            .strip()
            .split(",")[1]
            .strip()
            .rsplit(" ", 1)[-1]
            .strip()
        )

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        store_number = page_url.split("?StoreID=")[1].strip().split("-")[0].strip()
        phone = "".join(store.xpath('.//div[@class="store-phone"]/text()')).strip()

        location_type = "".join(
            store.xpath('div[@class="store-hours"]/p/strong/span/text()')
        ).strip()
        hours = store.xpath('div[@class="store-hours"]/p/text()')
        hours_of_operation = ""
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_of_operation = hours_of_operation + "".join(hour).strip() + " "
            else:
                break

        hours_of_operation = hours_of_operation.strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
