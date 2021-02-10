# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from lxml import etree
from bs4 import BeautifulSoup as BS

website = "musclemakergrill.com"
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

    search_url = "https://musclemakergrill.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@id="sidenav-locs"]/div[contains(@class,"col-md-12 item")]'
    )
    for store in stores:
        if len("".join(store.xpath('p[@class="item-coming"]/span/text()'))) <= 0:
            page_url = search_url
            locator_domain = website

            location_name = "".join(
                store.xpath('p[@class="item-title"]//text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            address = store.xpath("text()")
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())
                    break

            street_address = "".join(
                store.xpath('p[@class="item-address"]/text()')
            ).strip()
            if len(street_address) <= 0:
                street_address = "".join(store.xpath("div//text()")).strip()
                if len(street_address) <= 0:
                    street_address = "".join(
                        store.xpath('p[@class="p1"]/text()')
                    ).strip()

            street_address = " ".join(street_address.split("\n")).strip()
            if len(add_list[0].split(",")[1].strip().split(" ")) < 2:
                continue
            city = add_list[0].split(",")[0].strip()
            state = add_list[0].split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[0].split(",")[1].strip().split(" ")[1].strip()
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
            phone = ""
            phone_temp = store.xpath('.//a[contains(@href,"tel:")]/text()')
            if len(phone_temp) > 0:
                phone = phone_temp[0].strip()

            location_type = "<MISSING>"
            hours_of_operation = ""
            hours_list = []
            try:

                hours = BS(
                    str(etree.tostring(store))
                    .split("STORE HOURS:")[1]
                    .strip()
                    .split("</p>")[0]
                    .strip(),
                    "html.parser",
                ).get_text()

                hours = hours.split("\\n")
                for hour in hours:
                    if len("".join(hour)) > 0:
                        hours_list.append("".join(hour).strip())

            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = "".join(store.xpath("@data-lat")).strip()
            longitude = "".join(store.xpath("@data-lng")).strip()

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
