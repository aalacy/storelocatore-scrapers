# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us

website = "villageinn.com"
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

    search_url = "https://www.villageinn.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="columns nine locations-list"]/ul/li/a/@href'
    )
    for store_url in stores:
        page_url = store_url
        locator_domain = website
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(store_sel.xpath("//h1/text()")).strip()
        location_name = (
            location_name.encode("ascii", "replace")
            .strip()
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
            )
        ).strip()

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
        phone = "".join(store_sel.xpath('//a[@id="abrh-phone"]/text()')).strip()

        latitude = store_req.text.split("lat: ")[1].strip().split(",")[0].strip()

        longitude = store_req.text.split("lng: ")[1].strip().split("}")[0].strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = ""
        hours = store_sel.xpath('//ul[@class="hours"][1]/li')
        for hour in hours:
            day = "".join(hour.xpath("span/text()")).strip()
            time = "".join(hour.xpath("text()")).strip()
            hours_of_operation = hours_of_operation + day + time + " "

        hours_of_operation = (
            hours_of_operation.encode("ascii", "replace")
            .strip()
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
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
