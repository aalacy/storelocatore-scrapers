# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape import sgpostal as parser

website = "rush.co.uk"
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

    search_url = "https://www.rush.co.uk/salon-finder"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@class="accordion__item"]/a/@href')
    for store_url in stores:
        page_url = store_url
        log.info(store_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@itemprop="name"]/text()')
        ).strip()

        if location_name == "":
            location_name = "<MISSING>"

        raw_address = store_sel.xpath('//address[@class="sidebar__address"]')
        if len(raw_address) > 0:
            raw_address = ", ".join(raw_address[0].xpath("text()")).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = formatted_addr.country

            if country_code == "" or country_code is None:
                country_code = "<MISSING>"

            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zip == "" or zip is None:
                zip = "<MISSING>"

            phone = store_sel.xpath(
                '//div[@class="desktop-salon-actions"]/a[contains(@href,"tel:")]/text()'
            )
            if len(phone) > 0:
                phone = "".join(phone[0]).strip().replace("Call Us", "").strip()

            location_type = "<MISSING>"
            store_number = "<MISSING>"
            hours = store_sel.xpath(
                '//div[@class="salon_mobile_address_hours"]/div[2]//text()'
            )
            hours_list = []
            for hour in hours:
                if (
                    "mon:" in "".join(hour).strip().lower()
                    or "tue:" in "".join(hour).strip().lower()
                    or "wed:" in "".join(hour).strip().lower()
                    or "thu:" in "".join(hour).strip().lower()
                    or "fri:" in "".join(hour).strip().lower()
                    or "sat:" in "".join(hour).strip().lower()
                    or "sun:" in "".join(hour).strip().lower()
                ):
                    hours_list.append("".join(hour).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

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
