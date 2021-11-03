# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "smilestones.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://smilestones.ca/daycare-locations.htm"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@id="tab-1"]/div[./h1[contains(text(),"Locations")]]/div'
    )
    for store in stores:
        page_url = search_url
        locator_domain = website

        location_name = "".join(store.xpath("h2/text()")).strip()

        raw_info = "".join(store.xpath("div[2]/text()")).strip().split("\n")
        raw_list = []
        for index in range(0, len(raw_info) - 1):
            if len("".join(raw_info[index])) > 0:
                raw_list.append("".join(raw_info[index]))

        raw_address = ", ".join(raw_list).strip()
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        street_address = street_address.replace(". South", "").strip()
        city = location_name
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "CA"

        store_number = "<MISSING>"

        phone = raw_info[-1].strip().replace("Phone:", "").strip()

        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if location_name == "North Surrey":
            hours_of_operation = "Every Wednesday, 4:30pm"

        map_link = "".join(store.xpath('.//a[contains(@href,"maps")]/@href')).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(map_link) > 0:
            if "sll=" in map_link:
                latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
                longitude = (
                    map_link.split("sll=")[1]
                    .strip()
                    .split(",")[1]
                    .strip()
                    .split("&")[0]
                    .strip()
                )
            elif "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]

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
