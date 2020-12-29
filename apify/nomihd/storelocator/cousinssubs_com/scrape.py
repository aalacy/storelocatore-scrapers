# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import us
import lxml.html

website = "cousinssubs.com"
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

    search_url = "https://www.cousinssubs.com/find-a-store/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="more-info"]/@href')
    for store_url in stores:
        page_url = "https://www.cousinssubs.com" + store_url
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="row clearfix store-location"]/div/h2/text()')
        ).strip()

        if location_name == "":
            location_name = "<MISSING>"

        address = "".join(
            store_sel.xpath(
                '//div[@class="row clearfix store-location"]/div/div[@class="address"]/text()'
            )
        ).strip()

        street_address = address.split(",")[0].strip()
        city = address.split(",")[1]
        state = address.split(",")[2].strip().split(" ")[0].strip()
        zip = address.split(",")[2].strip().split(" ")[1].strip()

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
        phone = "".join(
            store_sel.xpath(
                '//div[@class="row clearfix store-location"]/div/div[@class="phone"]/text()'
            )
        ).strip()

        location_type = "<MISSING>"

        latitude = "".join(
            store_sel.xpath('//div[@class="distance"]/@data-lat')
        ).strip()
        longitude = "".join(
            store_sel.xpath('//div[@class="distance"]/@data-lon')
        ).strip()

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        hours = store_sel.xpath('//table[@class="hours"]/tr')
        hours_of_operation = ""
        for hour in hours:
            hours_of_operation = (
                hours_of_operation
                + "".join(hour.xpath("td[1]/text()")).strip()
                + ":"
                + "".join(hour.xpath("td[2]/div/text()")).strip()
                + " "
            )

        hours_of_operation = hours_of_operation.strip()

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
