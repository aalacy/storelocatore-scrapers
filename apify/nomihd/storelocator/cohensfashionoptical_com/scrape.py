# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "cohensfashionoptical.com"
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

    search_url = "https://www.cohensfashionoptical.com/all-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="fs-all-block"]')
    for store in stores:
        page_url = "".join(store.xpath('.//div[@class="fs-loc"]/h5/a/@href')).strip()
        locator_domain = website
        location_name = (
            "".join(store.xpath('.//div[@class="fs-loc"]/h5/a/text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store.xpath('.//div[@class="address"]/span[@class="street"]/text()')
        ).strip()
        city_state_zip = "".join(
            store.xpath('.//div[@class="address"]/span[@class="city_zip"]/text()')
        ).strip()

        city = city_state_zip.split(",")[0].strip()
        zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[-1].strip()
        state = city_state_zip.split(",")[1].strip().replace(zip, "").strip()

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

        store_number = "<MISSING>"
        phone = (
            "".join(store.xpath('.//div[@class="phone desktop"]/text()'))
            .strip()
            .replace("Call", "")
            .strip()
        )

        location_type = "OPEN"
        if (
            "Closed"
            in "".join(store.xpath('.//div[@class="loc-link"]/a/button/text()')).strip()
        ):
            location_type = "CLOSED"

        hours = store.xpath(
            './/div[@class="fs-store-hour"]/div[@class="day-hours-wrapper clearfix"]'
        )
        hours_of_operation = ""
        for hour in hours:
            day = "".join(hour.xpath('div[@class="display-days"]/text()')).strip()
            time = "".join(hour.xpath('div[@class="display-hours"]/text()')).strip()
            hours_of_operation = hours_of_operation + day + ":" + time + " "

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
