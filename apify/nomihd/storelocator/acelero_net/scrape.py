# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser
import re

website = "acelero.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def format_phone(s):
    return "" if s in " ().-" else s


def get_hours(lst):
    for x in lst:
        if ("AM" in x and "PM" in x) or ("am" in x and "pm" in x) and ":" in x:
            return x.strip()


def fetch_data():
    # Your scraper here
    search_url = "https://www.acelero.net/our-locations"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    locations_list = search_sel.xpath(
        "//h3/a/@href"
    )  # Location list from location's page

    for location in locations_list:
        location_res = session.get(location + "/our-centers", headers=headers)
        location_sel = lxml.html.fromstring(location_res.text)
        centers = location_sel.xpath(
            '//div[@class="image-caption"]'
        )  # centers on a location

        for center in centers:
            locator_domain = website
            full_description = center.xpath("./p[1]/text()")
            location_name = center.xpath("./p[1]//text()")[0]
            raw_address = " ".join(full_description).strip().split("Phone")[0].strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = (
                " ".join(full_description)
                .strip()
                .split("Phone:")[1]
                .strip()
                .split("Fax")[0]
                .strip()
            )

            phone = "".join(map(format_phone, phone))
            phone = re.split("[A-Za-z]", phone)[0]

            page_link = center.xpath("./p[1]/a/@href")[0].strip()
            center_page_link = (
                page_link if "http" in page_link else (location + page_link)
            )

            log.info(center_page_link)
            page_res = session.get(center_page_link, headers=headers)

            page_url = "<MISSING>" if page_res.status_code == 404 else center_page_link
            page_sel = lxml.html.fromstring(page_res.text)

            hrs_list = page_sel.xpath(
                '//div[@class="sqs-block-content"]//p[text()]/text()'
            )

            if hrs_list:
                hours_of_operation = get_hours(hrs_list)
            else:
                hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
