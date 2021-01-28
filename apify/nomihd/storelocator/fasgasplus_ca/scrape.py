# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "fasgasplus.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
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

    search_url = "https://fasgasplus.ca/station-directory/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//table[@class="contentTable zebra"]/tr[position()>1]')
    for store in stores:
        page_url = search_url
        locator_domain = website
        location_name = "".join(store.xpath("td[2]/text()")).strip()

        address = (
            "".join(store.xpath("td[3]/text()")).strip().replace("\xa0", "").strip()
        )

        street_address = address.rsplit(",", 1)[0].strip()
        city = location_name
        state = "".join(store.xpath('td[@class="hidden province"]/text()')).strip()

        zip = "".join(store.xpath('td[@class="hidden postalcode"]/text()')).strip()

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        country_code = "CA"
        if country_code == "":
            country_code = "<MISSING>"

        store_number = "<MISSING>"
        phone = "".join(store.xpath("td[4]/text()"))

        location_type = ""
        type = "".join(store.xpath('td[@class="hidden diesel"]/text()')).strip()
        if type == "1":
            location_type = "diesel"

        if location_type == "":
            location_type = "<MISSING>"

        hours = "".join(store.xpath('td[@class="hidden allday"]/text()')).strip()

        hours_of_operation = ""
        if hours == "1":
            hours_of_operation = "24 hours/7 days"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        latitude = "".join(store.xpath('td[@class="hidden latitude"]/text()')).strip()

        longitude = "".join(store.xpath('td[@class="hidden longitude"]/text()')).strip()

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
